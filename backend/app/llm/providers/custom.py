from openai import AsyncOpenAI
from app.llm.providers.base import BaseLLMProvider

class CustomProvider(BaseLLMProvider):
    def __init__(self, base_url: str, api_key: str = None, model: str = "default"):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key or "not-needed")
        self.model = model
    
    async def chat(self, messages: list[dict], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096)
        )
        
        return response.choices[0].message.content
    
    async def chat_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            temperature=kwargs.get("temperature", 0.7)
        )
        
        message = response.choices[0].message
        result = {"content": message.content or ""}
        
        if message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "input": tc.function.arguments
                }
                for tc in message.tool_calls
            ]
        
        return result
