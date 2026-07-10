import pytest
from app.llm.providers.base import BaseLLMProvider

def test_base_provider_interface():
    assert hasattr(BaseLLMProvider, "chat")
    assert hasattr(BaseLLMProvider, "chat_with_tools")
