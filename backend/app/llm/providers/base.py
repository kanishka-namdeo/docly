from abc import ABC, abstractmethod
from typing import Any

class BaseLLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> str:
        pass
    
    @abstractmethod
    async def chat_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> dict[str, Any]:
        pass
