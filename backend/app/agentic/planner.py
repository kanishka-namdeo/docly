import json
from typing import Any
from app.llm.client import LLMClient


class QueryPlanner:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def plan(self, query: str) -> dict[str, Any]:
        """
        Analyze query and determine if it needs decomposition.

        Returns dict with:
        - needs_decomposition: bool
        - sub_queries: list[str]
        - reasoning: str
        """
        system_prompt = """You are a query analyzer. Determine if the user's question needs to be broken down into sub-queries.

Simple queries (single concept, direct lookup) do NOT need decomposition.
Complex queries (multiple concepts, comparisons, multi-step reasoning) DO need decomposition.

Respond with JSON:
{
    "needs_decomposition": true/false,
    "sub_queries": ["query1", "query2"] or ["original_query"],
    "reasoning": "brief explanation"
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        response = await self.llm.chat(messages, temperature=0.3)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            # Fallback: assume no decomposition needed
            result = {
                "needs_decomposition": False,
                "sub_queries": [query],
                "reasoning": "Failed to parse response, using original query",
            }

        return result
