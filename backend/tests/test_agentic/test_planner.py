import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agentic.planner import QueryPlanner


@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    llm = MagicMock()
    llm.chat = AsyncMock()
    return llm


class TestQueryPlanner:
    """Test suite for QueryPlanner."""

    @pytest.mark.asyncio
    async def test_planner_simple_query(self, mock_llm):
        """Test that simple queries are not decomposed."""
        mock_llm.chat.return_value = json.dumps({
            "needs_decomposition": False,
            "sub_queries": ["What is machine learning?"],
            "reasoning": "Single concept query, no decomposition needed",
        })

        planner = QueryPlanner(mock_llm)
        result = await planner.plan("What is machine learning?")

        assert result["needs_decomposition"] is False
        assert len(result["sub_queries"]) == 1
        assert result["sub_queries"][0] == "What is machine learning?"

    @pytest.mark.asyncio
    async def test_planner_complex_query(self, mock_llm):
        """Test that complex queries are decomposed."""
        mock_llm.chat.return_value = json.dumps({
            "needs_decomposition": True,
            "sub_queries": [
                "What is machine learning?",
                "What is deep learning?",
                "What is the difference between machine learning and deep learning?",
            ],
            "reasoning": "Multiple concepts requiring comparison",
        })

        planner = QueryPlanner(mock_llm)
        result = await planner.plan(
            "What is the difference between machine learning and deep learning?"
        )

        assert result["needs_decomposition"] is True
        assert len(result["sub_queries"]) == 3
        assert "reasoning" in result

    @pytest.mark.asyncio
    async def test_planner_json_decode_error_fallback(self, mock_llm):
        """Test fallback behavior when LLM returns invalid JSON."""
        mock_llm.chat.return_value = "Not valid JSON at all"

        planner = QueryPlanner(mock_llm)
        result = await planner.plan("Test query")

        assert result["needs_decomposition"] is False
        assert result["sub_queries"] == ["Test query"]
        assert "Failed to parse" in result["reasoning"]

    @pytest.mark.asyncio
    async def test_planner_returns_all_fields(self, mock_llm):
        """Test that planner returns all required fields."""
        mock_llm.chat.return_value = json.dumps({
            "needs_decomposition": False,
            "sub_queries": ["Test?"],
            "reasoning": "Simple query",
        })

        planner = QueryPlanner(mock_llm)
        result = await planner.plan("Test?")

        assert "needs_decomposition" in result
        assert "sub_queries" in result
        assert "reasoning" in result
        assert isinstance(result["needs_decomposition"], bool)
        assert isinstance(result["sub_queries"], list)
        assert isinstance(result["reasoning"], str)
