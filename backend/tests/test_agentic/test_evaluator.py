import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agentic.evaluator import RetrievalEvaluator


@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    llm = MagicMock()
    llm.chat = AsyncMock()
    return llm


class TestRetrievalEvaluator:
    """Test suite for RetrievalEvaluator."""

    @pytest.mark.asyncio
    async def test_evaluator_high_confidence(self, mock_llm):
        """Test that relevant chunks get high confidence."""
        mock_llm.chat.return_value = json.dumps({
            "confidence": "high",
            "score": 0.95,
            "reasoning": "Chunks directly and fully answer the question",
        })

        evaluator = RetrievalEvaluator(mock_llm)
        query = "What is machine learning?"
        chunks = [
            {
                "text": "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
                "score": 0.95,
            }
        ]

        result = await evaluator.evaluate(query, chunks)

        assert result["confidence"] == "high"
        assert result["score"] >= 0.8

    @pytest.mark.asyncio
    async def test_evaluator_medium_confidence(self, mock_llm):
        """Test that partially relevant chunks get medium confidence."""
        mock_llm.chat.return_value = json.dumps({
            "confidence": "medium",
            "score": 0.6,
            "reasoning": "Chunks partially answer the question",
        })

        evaluator = RetrievalEvaluator(mock_llm)
        chunks = [
            {"text": "AI is a broad field of computer science.", "score": 0.5}
        ]

        result = await evaluator.evaluate("What is machine learning?", chunks)

        assert result["confidence"] == "medium"
        assert 0.5 <= result["score"] < 0.8

    @pytest.mark.asyncio
    async def test_evaluator_low_confidence(self, mock_llm):
        """Test that irrelevant chunks get low confidence."""
        mock_llm.chat.return_value = json.dumps({
            "confidence": "low",
            "score": 0.2,
            "reasoning": "Chunks are irrelevant",
        })

        evaluator = RetrievalEvaluator(mock_llm)
        chunks = [
            {"text": "The weather today is sunny.", "score": 0.1}
        ]

        result = await evaluator.evaluate("What is machine learning?", chunks)

        assert result["confidence"] == "low"
        assert result["score"] < 0.5

    @pytest.mark.asyncio
    async def test_evaluator_no_chunks(self, mock_llm):
        """Test that empty chunk list returns low confidence without LLM call."""
        evaluator = RetrievalEvaluator(mock_llm)
        result = await evaluator.evaluate("What is ML?", [])

        assert result["confidence"] == "low"
        assert result["score"] == 0.0
        assert "No chunks" in result["reasoning"]
        mock_llm.chat.assert_not_called()

    @pytest.mark.asyncio
    async def test_evaluator_json_decode_error_fallback(self, mock_llm):
        """Test fallback behavior when LLM returns invalid JSON."""
        mock_llm.chat.return_value = "Invalid JSON"

        evaluator = RetrievalEvaluator(mock_llm)
        chunks = [
            {"text": "Some text about ML.", "score": 0.8},
            {"text": "More ML text.", "score": 0.7},
        ]

        result = await evaluator.evaluate("What is ML?", chunks)

        # Fallback uses average score
        assert result["score"] == 0.75  # (0.8 + 0.7) / 2
        assert "Failed to parse" in result["reasoning"]

    @pytest.mark.asyncio
    async def test_evaluator_limits_to_five_chunks(self, mock_llm):
        """Test that only top 5 chunks are sent for evaluation."""
        mock_llm.chat.return_value = json.dumps({
            "confidence": "high",
            "score": 0.9,
            "reasoning": "Good coverage",
        })

        evaluator = RetrievalEvaluator(mock_llm)
        chunks = [
            {"text": f"Chunk {i}", "score": 0.9} for i in range(10)
        ]

        await evaluator.evaluate("Query?", chunks)

        # Check the prompt was constructed with limited chunks
        call_args = mock_llm.chat.call_args
        messages = call_args[0][0]
        user_content = messages[1]["content"]
        # Should only have Chunk 1 through Chunk 5
        assert "Chunk 1" in user_content
        assert "Chunk 5" in user_content
        assert "Chunk 6" not in user_content

    @pytest.mark.asyncio
    async def test_evaluator_returns_all_fields(self, mock_llm):
        """Test that evaluator returns all required fields."""
        mock_llm.chat.return_value = json.dumps({
            "confidence": "high",
            "score": 0.9,
            "reasoning": "Good",
        })

        evaluator = RetrievalEvaluator(mock_llm)
        result = await evaluator.evaluate("Q?", [{"text": "A", "score": 0.9}])

        assert "confidence" in result
        assert "score" in result
        assert "reasoning" in result
        assert result["confidence"] in ("high", "medium", "low")
        assert isinstance(result["score"], float)
        assert isinstance(result["reasoning"], str)
