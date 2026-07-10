import json
from typing import Any
from app.llm.client import LLMClient


class RetrievalEvaluator:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def evaluate(self, query: str, chunks: list[dict]) -> dict[str, Any]:
        """
        Evaluate retrieval quality and determine confidence level.

        Returns dict with:
        - confidence: "high" | "medium" | "low"
        - score: float (0-1)
        - reasoning: str
        """
        if not chunks:
            return {
                "confidence": "low",
                "score": 0.0,
                "reasoning": "No chunks retrieved",
            }

        # Prepare chunks for evaluation
        chunks_text = "\n\n".join(
            [
                f"[Chunk {i+1}] (score: {c.get('score', 0):.2f})\n{c['text']}"
                for i, c in enumerate(chunks[:5])  # Evaluate top 5
            ]
        )

        system_prompt = """You are a retrieval quality evaluator. Assess whether the retrieved chunks adequately answer the user's question.

Consider:
- Relevance: Do the chunks directly address the question?
- Completeness: Is there enough information to provide a good answer?
- Quality: Are the chunks clear and well-structured?

Respond with JSON:
{
    "confidence": "high" | "medium" | "low",
    "score": 0.0-1.0,
    "reasoning": "brief explanation"
}

High confidence (0.8-1.0): Chunks directly and fully answer the question
Medium confidence (0.5-0.79): Chunks partially answer or need some inference
Low confidence (0.0-0.49): Chunks are irrelevant or insufficient"""

        user_prompt = f"Question: {query}\n\nRetrieved chunks:\n{chunks_text}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = await self.llm.chat(messages, temperature=0.2)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            # Fallback: use average score
            avg_score = sum(c.get("score", 0) for c in chunks) / len(chunks)
            result = {
                "confidence": "medium" if avg_score > 0.7 else "low",
                "score": avg_score,
                "reasoning": "Failed to parse response, using average score",
            }

        return result
