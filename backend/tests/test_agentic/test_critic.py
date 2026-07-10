import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agentic.critic import SelfCritic


@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    llm = MagicMock()
    llm.chat = AsyncMock()
    return llm


class TestSelfCritic:
    """Test suite for SelfCritic."""

    @pytest.mark.asyncio
    async def test_critic_valid_answer(self, mock_llm):
        """Test that supported answers pass validation."""
        mock_llm.chat.return_value = json.dumps({
            "is_supported": True,
            "score": 0.95,
            "reasoning": "All claims are supported by sources",
            "hallucinations": [],
        })

        critic = SelfCritic(mock_llm)
        query = "What is machine learning?"
        answer = (
            "Machine learning is a subset of AI that enables systems to learn from data."
        )
        chunks = [
            {
                "text": "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
                "score": 0.95,
            }
        ]

        result = await critic.critique(query, answer, chunks)

        assert result["is_supported"] is True
        assert result["score"] >= 0.8

    @pytest.mark.asyncio
    async def test_critic_detects_hallucination(self, mock_llm):
        """Test that unsupported claims are detected."""
        mock_llm.chat.return_value = json.dumps({
            "is_supported": False,
            "score": 0.3,
            "reasoning": "Answer contains unsupported claims",
            "hallucinations": ["ML was invented in 1950 by Alan Turing"],
        })

        critic = SelfCritic(mock_llm)
        chunks = [
            {
                "text": "Machine learning is a subset of artificial intelligence.",
                "score": 0.9,
            }
        ]

        result = await critic.critique(
            "Who invented ML?", "ML was invented in 1950 by Alan Turing.", chunks
        )

        assert result["is_supported"] is False
        assert len(result["hallucinations"]) > 0
        assert result["score"] < 0.5

    @pytest.mark.asyncio
    async def test_critic_partial_support(self, mock_llm):
        """Test that partially supported answers get medium score."""
        mock_llm.chat.return_value = json.dumps({
            "is_supported": True,
            "score": 0.6,
            "reasoning": "Mostly supported but some minor extrapolation",
            "hallucinations": [],
        })

        critic = SelfCritic(mock_llm)
        chunks = [
            {"text": "Python is a programming language.", "score": 0.8}
        ]

        result = await critic.critique(
            "Tell me about Python", "Python is a programming language popular for ML.", chunks
        )

        assert 0.5 <= result["score"] < 0.8
        assert isinstance(result["is_supported"], bool)

    @pytest.mark.asyncio
    async def test_critic_json_decode_error_fallback(self, mock_llm):
        """Test fallback behavior when LLM returns invalid JSON."""
        mock_llm.chat.return_value = "Not JSON"

        critic = SelfCritic(mock_llm)
        result = await critic.critique("Q?", "A?", [{"text": "Source", "score": 0.9}])

        assert result["is_supported"] is True
        assert result["score"] == 0.7
        assert "Failed to parse" in result["reasoning"]
        assert result["hallucinations"] == []

    @pytest.mark.asyncio
    async def test_critic_returns_all_fields(self, mock_llm):
        """Test that critic returns all required fields."""
        mock_llm.chat.return_value = json.dumps({
            "is_supported": True,
            "score": 0.9,
            "reasoning": "Good answer",
            "hallucinations": [],
        })

        critic = SelfCritic(mock_llm)
        result = await critic.critique("Q?", "A?", [{"text": "S", "score": 0.9}])

        assert "is_supported" in result
        assert "score" in result
        assert "reasoning" in result
        assert "hallucinations" in result
        assert isinstance(result["is_supported"], bool)
        assert isinstance(result["score"], float)
        assert isinstance(result["reasoning"], str)
        assert isinstance(result["hallucinations"], list)

    @pytest.mark.asyncio
    async def test_critic_empty_chunks(self, mock_llm):
        """Test critic behavior with no source chunks."""
        mock_llm.chat.return_value = json.dumps({
            "is_supported": False,
            "score": 0.0,
            "reasoning": "No sources to verify against",
            "hallucinations": ["Entire answer is unverifiable"],
        })

        critic = SelfCritic(mock_llm)
        result = await critic.critique("Q?", "Some answer", [])

        # With no chunks, the LLM should flag everything as unsupported
        assert result["is_supported"] is False
        assert result["score"] == 0.0
