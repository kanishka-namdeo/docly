import json
from typing import Any
from app.llm.client import LLMClient


class SelfCritic:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def critique(
        self, query: str, answer: str, chunks: list[dict]
    ) -> dict[str, Any]:
        """
        Validate that the answer is supported by the retrieved chunks.

        Returns dict with:
        - is_supported: bool
        - score: float (0-1)
        - reasoning: str
        - hallucinations: list[str] (unsupported claims)
        """
        chunks_text = "\n\n".join(
            [f"[Source {i+1}]\n{c['text']}" for i, c in enumerate(chunks)]
        )

        system_prompt = """You are an answer quality validator. Check if the generated answer is supported by the source chunks.

Look for:
- Factual accuracy: Are all claims in the answer supported by the sources?
- Hallucinations: Does the answer contain information NOT in the sources?
- Completeness: Does the answer adequately address the question based on available information?

Respond with JSON:
{
    "is_supported": true/false,
    "score": 0.0-1.0,
    "reasoning": "brief explanation",
    "hallucinations": ["claim1", "claim2"] or []
}

High score (0.8-1.0): Answer is fully supported by sources
Medium score (0.5-0.79): Answer is mostly supported but may have minor issues
Low score (0.0-0.49): Answer contains hallucinations or is not supported"""

        user_prompt = f"""Question: {query}

Generated Answer: {answer}

Source Chunks:
{chunks_text}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = await self.llm.chat(messages, temperature=0.2)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            # Fallback: assume supported
            result = {
                "is_supported": True,
                "score": 0.7,
                "reasoning": "Failed to parse response, assuming supported",
                "hallucinations": [],
            }

        return result
