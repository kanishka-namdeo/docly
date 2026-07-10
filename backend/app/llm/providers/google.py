import google.generativeai as genai
from app.llm.providers.base import BaseLLMProvider

class GoogleProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    async def chat(self, messages: list[dict], **kwargs) -> str:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        
        response = await self.model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=kwargs.get("temperature", 0.7),
                max_output_tokens=kwargs.get("max_tokens", 4096)
            )
        )
        
        return response.text
    
    async def chat_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> dict:
        response = await self.chat(messages, **kwargs)
        return {"content": response}
