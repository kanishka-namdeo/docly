from anthropic import AsyncAnthropic
from app.llm.providers.base import BaseLLMProvider

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
    
    async def chat(self, messages: list[dict], **kwargs) -> str:
        system_msg = None
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append(msg)
        
        response = await self.client.messages.create(
            model=self.model,
            system=system_msg or "",
            messages=chat_messages,
            max_tokens=kwargs.get("max_tokens", 4096),
            temperature=kwargs.get("temperature", 0.7)
        )
        
        return response.content[0].text
    
    async def chat_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> dict:
        system_msg = None
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append(msg)
        
        response = await self.client.messages.create(
            model=self.model,
            system=system_msg or "",
            messages=chat_messages,
            tools=tools,
            max_tokens=kwargs.get("max_tokens", 4096)
        )
        
        result = {"content": ""}
        
        for block in response.content:
            if block.type == "text":
                result["content"] += block.text
            elif block.type == "tool_use":
                if "tool_calls" not in result:
                    result["tool_calls"] = []
                result["tool_calls"].append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })
        
        return result
