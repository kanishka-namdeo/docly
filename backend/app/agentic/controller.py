from typing import Any
from app.llm.client import LLMClient
from app.retrieval.hybrid_search import HybridSearch
from app.agentic.planner import QueryPlanner
from app.agentic.evaluator import RetrievalEvaluator
from app.agentic.critic import SelfCritic


import json
from typing import Any
from app.llm.client import LLMClient
from app.retrieval.hybrid_search import HybridSearch
from app.agentic.planner import QueryPlanner
from app.agentic.evaluator import RetrievalEvaluator
from app.agentic.critic import SelfCritic

# Tool definitions for agentic RAG
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search for relevant documents in the knowledge base",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)"
                    }
                },
                "required": ["query"]
            }
        }
    }
]
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
    async def process(
        self,
        query: str,
        collection_id: str = None,
        conversation_history: list[dict] = None,
    ) -> dict[str, Any]:
        """
        Process a query through the agentic RAG loop with tool calling.

        Returns dict with:
        - answer: str
        - citations: list[dict]
        - iterations: int
        - reasoning: str
        """
        iteration = 0
        all_citations = []
        reasoning_steps = []
        
        # Initial message
        messages = [{"role": "user", "content": query}]
        
        # Tool calling loop
        while iteration < self.max_iterations:
            iteration += 1
            
            # Call LLM with tools
            response = await self.llm.chat_with_tools(messages, TOOLS)
            
            # Check if LLM wants to call a tool
            if response.get("tool_calls"):
                tool_calls = response["tool_calls"]
                reasoning_steps.append(f"Iteration {iteration}: Calling {len(tool_calls)} tool(s)")
                
                # Execute each tool call
                for tool_call in tool_calls:
                    if tool_call["function"]["name"] == "search_documents":
                        try:
                            args = json.loads(tool_call["function"]["arguments"])
                            search_query = args.get("query", query)
                            limit = args.get("limit", 10)
                            
                            # Execute search
                            chunks = await self.search.search(
                                search_query, limit=limit, collection_id=collection_id
                            )
                            
                            reasoning_steps.append(f"  Searched for: {search_query}, found {len(chunks)} results")
                            
                            # Add results to citations
                            for chunk in chunks[:3]:
                                all_citations.append({
                                    "text": chunk["text"],
                                    "file_path": chunk["file_path"],
                                    "document_id": chunk["document_id"],
                                    "chunk_index": chunk["chunk_index"],
                                    "score": chunk["score"],
                                    "parent_context": chunk.get("parent_context", ""),
                                })
                            
                            # Add tool result to messages
                            tool_result = {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": json.dumps([
                                    {"text": c["text"][:500], "score": c["score"]}
                                    for c in chunks[:5]
                                ])
                            }
                            messages.append(tool_result)
                            
                        except Exception as e:
                            reasoning_steps.append(f"  Tool execution failed: {str(e)}")
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": json.dumps({"error": str(e)})
                            })
                
                # Continue loop to let LLM process tool results
                continue
            
            # No tool calls - LLM is providing final answer
            final_answer = response.get("content", "")
            reasoning_steps.append(f"Iteration {iteration}: Generated final answer")
            break
        
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
