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

    async def reformulate(self, original_query: str, feedback: str, context: dict = None) -> str:
        """
        Reformulate a query based on retrieval feedback.
        
        Args:
            original_query: The original query that had low confidence
            feedback: Feedback from the evaluator about why confidence was low
            context: Optional context about the retrieval attempt
        
        Returns:
            Reformulated query string
        """
        system_prompt = """You are a query reformulator. Your job is to improve queries that failed to retrieve good results.

Given the original query and feedback about why it failed, create a better query that is:
- More specific and focused
- Uses different terminology if needed
- Breaks down complex concepts
- Removes ambiguity

Respond with ONLY the reformulated query, nothing else."""

        user_prompt = f"""Original query: {original_query}

Feedback: {feedback}

{f'Context: {context}' if context else ''}

Reformulated query:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = await self.llm.chat(messages, temperature=0.5)
        
        # Clean up response
        reformulated = response.strip().strip('"').strip("'")
        
        # Fallback to original if reformulation is empty or too short
        if not reformulated or len(reformulated) < 3:
            return original_query
        
        return reformulated
