import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.llm.client import LLMClient
from app.llm.providers.anthropic import AnthropicProvider
from app.llm.providers.openai import OpenAIProvider
from app.llm.providers.google import GoogleProvider
from app.llm.providers.custom import CustomProvider

def test_llm_client_openai_provider():
    """Test LLMClient creates OpenAIProvider for openai type."""
    config = {"type": "openai", "api_key": "test-key", "model": "gpt-4o"}
    client = LLMClient(config)
    assert isinstance(client.provider, OpenAIProvider)

def test_llm_client_anthropic_provider():
    """Test LLMClient creates AnthropicProvider for anthropic type."""
    config = {"type": "anthropic", "api_key": "test-key", "model": "claude-3-5-sonnet-20241022"}
    client = LLMClient(config)
    assert isinstance(client.provider, AnthropicProvider)

def test_llm_client_custom_provider():
    """Test LLMClient creates CustomProvider for custom type."""
    config = {"type": "custom", "base_url": "http://localhost:8080", "api_key": "test-key", "model": "llama"}
    client = LLMClient(config)
    assert isinstance(client.provider, CustomProvider)

def test_llm_client_unknown_provider():
    """Test LLMClient raises ValueError for unknown provider type."""
    config = {"type": "unknown", "api_key": "test-key"}
    with pytest.raises(ValueError, match="Unknown provider type: unknown"):
        LLMClient(config)

@pytest.mark.asyncio
async def test_llm_client_chat_delegates():
    """Test that chat() delegates to provider."""
    config = {"type": "openai", "api_key": "test-key", "model": "gpt-4o"}
    client = LLMClient(config)
    
    mock_response = AsyncMock(return_value="Hello!")
    client.provider.chat = mock_response
    
    messages = [{"role": "user", "content": "Hi"}]
    result = await client.chat(messages, temperature=0.5)
    
    mock_response.assert_called_once_with(messages, temperature=0.5)
    assert result == "Hello!"

@pytest.mark.asyncio
async def test_llm_client_chat_with_tools_delegates():
    """Test that chat_with_tools() delegates to provider."""
    config = {"type": "openai", "api_key": "test-key", "model": "gpt-4o"}
    client = LLMClient(config)
    
    mock_response = AsyncMock(return_value={"content": "result", "tool_calls": []})
    client.provider.chat_with_tools = mock_response
    
    messages = [{"role": "user", "content": "Search"}]
    tools = [{"name": "search"}]
    result = await client.chat_with_tools(messages, tools, temperature=0.3)
    
    mock_response.assert_called_once_with(messages, tools, temperature=0.3)
    assert result == {"content": "result", "tool_calls": []}
