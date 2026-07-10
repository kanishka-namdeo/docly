from typing import Any
from app.llm.client import LLMClient
from app.retrieval.hybrid_search import HybridSearch
from app.agentic.planner import QueryPlanner
from app.agentic.evaluator import RetrievalEvaluator
from app.agentic.critic import SelfCritic


class AgenticController:
    def __init__(
        self,
        llm: LLMClient,
        search: HybridSearch,
        max_iterations: int = 5,
    ):
        self.llm = llm
        self.search = search
        self.max_iterations = max_iterations
        self.planner = QueryPlanner(llm)
        self.evaluator = RetrievalEvaluator(llm)
        self.critic = SelfCritic(llm)

    async def process(
        self,
        query: str,
        collection_id: str = None,
        conversation_history: list[dict] = None,
    ) -> dict[str, Any]:
        """
        Process a query through the agentic RAG loop.

        Returns dict with:
        - answer: str
        - citations: list[dict]
        - iterations: int
        - reasoning: str
        """
        iteration = 0
        all_citations = []
        reasoning_steps = []

        # Step 1: Plan query
        plan = await self.planner.plan(query)
        reasoning_steps.append(f"Planning: {plan['reasoning']}")

        sub_queries = plan["sub_queries"]

        # Step 2: Process each sub-query
        for sub_query in sub_queries:
            if iteration >= self.max_iterations:
                break

            # Retrieve chunks
            chunks = await self.search.search(
                sub_query, limit=10, collection_id=collection_id
            )

            if not chunks:
                reasoning_steps.append(f"No results for: {sub_query}")
                continue

            # Evaluate retrieval quality
            evaluation = await self.evaluator.evaluate(sub_query, chunks)
            reasoning_steps.append(f"Evaluation: {evaluation['reasoning']}")

            # If low confidence, could refine query (simplified: just continue)
            if evaluation["confidence"] == "low":
                reasoning_steps.append(
                    "Low confidence, but continuing with available chunks"
                )

            # Generate answer for this sub-query
            answer = await self._generate_answer(
                sub_query, chunks, conversation_history
            )

            # Self-critique
            critique = await self.critic.critique(sub_query, answer, chunks)
            reasoning_steps.append(f"Critique: {critique['reasoning']}")

            # If answer is supported, add to results
            if critique["is_supported"]:
                all_citations.extend(
                    [
                        {
                            "text": chunk["text"],
                            "file_path": chunk["file_path"],
                            "document_id": chunk["document_id"],
                            "chunk_index": chunk["chunk_index"],
                            "score": chunk["score"],
                            "parent_context": chunk.get("parent_context", ""),
                        }
                        for chunk in chunks[:3]  # Top 3 citations
                    ]
                )

            iteration += 1

        # Step 3: Generate final answer
        final_answer = await self._generate_final_answer(
            query, all_citations, conversation_history
        )

        return {
            "answer": final_answer,
            "citations": all_citations,
            "iterations": iteration,
            "reasoning": "\n".join(reasoning_steps),
        }

    async def _generate_answer(
        self, query: str, chunks: list[dict], history: list[dict] = None
    ) -> str:
        """Generate answer for a sub-query."""
        context = "\n\n".join([c["text"] for c in chunks[:5]])

        system_prompt = """You are a helpful assistant. Answer the question based on the provided context.
Be concise and accurate. Cite sources using [1], [2], etc."""

        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history[-10:])  # Last 10 messages

        messages.append(
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}",
            }
        )

        return await self.llm.chat(messages, temperature=0.7)

    async def _generate_final_answer(
        self, query: str, citations: list[dict], history: list[dict] = None
    ) -> str:
        """Generate final comprehensive answer."""
        if not citations:
            return "I couldn't find relevant information to answer your question."

        context = "\n\n".join([c["text"] for c in citations[:5]])

        system_prompt = """You are a helpful assistant. Provide a comprehensive answer to the question based on the provided context.
Use citations [1], [2], etc. to reference sources. Be clear and well-structured."""

        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history[-10:])

        messages.append(
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}",
            }
        )

        return await self.llm.chat(messages, temperature=0.7)
