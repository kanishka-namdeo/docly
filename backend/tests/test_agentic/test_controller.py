import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agentic.controller import AgenticController


@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    llm = MagicMock()
    llm.chat = AsyncMock()

    def chat_side_effect(messages, **kwargs):
        """Route responses based on message content."""
        user_content = ""
        for msg in messages:
            if msg["role"] == "user":
                user_content = msg["content"]

        # Planner responses
        if "query analyzer" in str(messages[0]).lower():
            return json.dumps({
                "needs_decomposition": False,
                "sub_queries": ["What is machine learning?"],
                "reasoning": "Simple query",
            })

        # Evaluator responses
        if "retrieval quality evaluator" in str(messages[0]).lower():
            return json.dumps({
                "confidence": "high",
                "score": 0.9,
                "reasoning": "Chunks directly answer the question",
            })

        # Critic responses
        if "answer quality validator" in str(messages[0]).lower():
            return json.dumps({
                "is_supported": True,
                "score": 0.9,
                "reasoning": "Answer is fully supported",
                "hallucinations": [],
            })

        # Generator responses (both sub-query and final)
        if "helpful assistant" in str(messages[0]).lower():
            if "comprehensive answer" in str(messages[0]).lower():
                return "Machine learning is a subset of AI that enables systems to learn from data [1]."
            return "Machine learning is a subset of AI."

        return "Default response"

    llm.chat.side_effect = chat_side_effect
    return llm


@pytest.fixture
def mock_search():
    """Create a mock search engine."""
    search = MagicMock()
    search.search = AsyncMock()
    search.search.return_value = [
        {
            "text": "Machine learning is a subset of AI.",
            "score": 0.9,
            "file_path": "test.md",
            "collection_id": "test",
            "document_id": "doc1",
            "chunk_index": 0,
            "parent_context": "Machine learning is a subset of AI.",
        }
    ]
    return search


class TestAgenticController:
    """Test suite for AgenticController."""

    @pytest.mark.asyncio
    async def test_controller_basic_query(self, mock_llm, mock_search):
        """Test basic query processing through agentic loop."""
        controller = AgenticController(mock_llm, mock_search)

        result = await controller.process("What is machine learning?")

        assert "answer" in result
        assert "citations" in result
        assert "iterations" in result
        assert result["iterations"] <= 5
        assert "reasoning" in result
        assert isinstance(result["citations"], list)
        assert isinstance(result["reasoning"], str)

    @pytest.mark.asyncio
    async def test_controller_returns_citations(self, mock_llm, mock_search):
        """Test that controller returns citations from chunks."""
        controller = AgenticController(mock_llm, mock_search)

        result = await controller.process("What is machine learning?")

        assert len(result["citations"]) > 0
        citation = result["citations"][0]
        assert "text" in citation
        assert "file_path" in citation
        assert "document_id" in citation
        assert "chunk_index" in citation
        assert "score" in citation
        assert "parent_context" in citation

    @pytest.mark.asyncio
    async def test_controller_no_results(self, mock_llm):
        """Test controller behavior when search returns no results."""
        search = MagicMock()
        search.search = AsyncMock(return_value=[])

        controller = AgenticController(mock_llm, search)
        result = await controller.process("What is quantum computing?")

        assert "answer" in result
        # Should get the fallback answer since no citations
        assert "couldn't find" in result["answer"].lower() or result["iterations"] == 0

    @pytest.mark.asyncio
    async def test_controller_max_iterations(self, mock_llm):
        """Test that controller respects max_iterations."""
        # Planner returns multiple sub-queries
        original_side_effect = mock_llm.chat.side_effect

        def side_effect_with_decomposition(messages, **kwargs):
            user_content = ""
            for msg in messages:
                if msg["role"] == "user":
                    user_content = msg["content"]

            if "query analyzer" in str(messages[0]).lower():
                return json.dumps({
                    "needs_decomposition": True,
                    "sub_queries": [
                        f"Sub-query {i}" for i in range(10)
                    ],
                    "reasoning": "Complex multi-part query",
                })
            return original_side_effect(messages, **kwargs)

        mock_llm.chat.side_effect = side_effect_with_decomposition

        search = MagicMock()
        search.search = AsyncMock(return_value=[
            {
                "text": "Test result",
                "score": 0.9,
                "file_path": "test.md",
                "collection_id": "test",
                "document_id": "doc1",
                "chunk_index": 0,
                "parent_context": "Test",
            }
        ])

        controller = AgenticController(mock_llm, search, max_iterations=5)
        result = await controller.process("Complex question")

        assert result["iterations"] <= 5

    @pytest.mark.asyncio
    async def test_controller_with_collection_id(self, mock_llm, mock_search):
        """Test controller passes collection_id to search."""
        controller = AgenticController(mock_llm, mock_search)

        await controller.process(
            "What is ML?", collection_id="my_collection"
        )

        mock_search.search.assert_called()
        call_kwargs = mock_search.search.call_args
        assert call_kwargs[1]["collection_id"] == "my_collection"

    @pytest.mark.asyncio
    async def test_controller_with_conversation_history(self, mock_llm, mock_search):
        """Test controller passes conversation history to generators."""
        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
        ]

        controller = AgenticController(mock_llm, mock_search)
        result = await controller.process(
            "What is ML?", conversation_history=history
        )

        assert "answer" in result

    @pytest.mark.asyncio
    async def test_controller_includes_reasoning_steps(self, mock_llm, mock_search):
        """Test that reasoning trace is populated."""
        controller = AgenticController(mock_llm, mock_search)
        result = await controller.process("What is machine learning?")

        assert result["reasoning"]
        assert "Planning:" in result["reasoning"]

    @pytest.mark.asyncio
    async def test_controller_low_confidence_continues(self, mock_llm, mock_search):
        """Test controller continues even with low confidence retrieval."""
        original_side_effect = mock_llm.chat.side_effect

        def side_effect_low_confidence(messages, **kwargs):
            if "retrieval quality evaluator" in str(messages[0]).lower():
                return json.dumps({
                    "confidence": "low",
                    "score": 0.3,
                    "reasoning": "Chunks are tangentially related",
                })
            return original_side_effect(messages, **kwargs)

        mock_llm.chat.side_effect = side_effect_low_confidence

        controller = AgenticController(mock_llm, mock_search)
        result = await controller.process("What is ML?")

        # Should still produce an answer despite low confidence
        assert "answer" in result
        assert "Low confidence" in result["reasoning"]

    @pytest.mark.asyncio
    async def test_controller_unsupported_answer_excluded(self, mock_llm, mock_search):
        """Test that unsupported answers don't add citations."""
        original_side_effect = mock_llm.chat.side_effect

        def side_effect_unsupported(messages, **kwargs):
            if "answer quality validator" in str(messages[0]).lower():
                return json.dumps({
                    "is_supported": False,
                    "score": 0.2,
                    "reasoning": "Answer contains unsupported claims",
                    "hallucinations": ["Made up fact"],
                })
            return original_side_effect(messages, **kwargs)

        mock_llm.chat.side_effect = side_effect_unsupported

        controller = AgenticController(mock_llm, mock_search)
        result = await controller.process("What is ML?")

        # Citations should be empty when answer is not supported
        assert result["citations"] == []
