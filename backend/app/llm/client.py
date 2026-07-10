from typing import Any
from app.llm.providers.base import BaseLLMProvider
from app.llm.providers.anthropic import AnthropicProvider
from app.llm.providers.openai import OpenAIProvider
from app.llm.providers.google import GoogleProvider
from app.llm.providers.custom import CustomProvider

class LLMClient:
    def __init__(self, provider_config: dict):
        provider_type = provider_config["type"]
        api_key = provider_config.get("api_key")
        model = provider_config.get("model")
        
        if provider_type == "anthropic":
            self.provider = AnthropicProvider(api_key=api_key, model=model)
        elif provider_type == "openai":
            self.provider = OpenAIProvider(api_key=api_key, model=model)
        elif provider_type == "google":
            self.provider = GoogleProvider(api_key=api_key, model=model)
        elif provider_type == "custom":
            base_url = provider_config.get("base_url")
            self.provider = CustomProvider(base_url=base_url, api_key=api_key, model=model)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    async def chat(self, messages: list[dict], **kwargs) -> str:
        return await self.provider.chat(messages, **kwargs)
    
    async def chat_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> dict[str, Any]:
        return await self.provider.chat_with_tools(messages, tools, **kwargs)
