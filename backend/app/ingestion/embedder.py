import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class LMStudioEmbedder:
    def __init__(self, base_url: str = "http://localhost:1234", model: str = "text-embedding-nomic-embed-text-v1.5"):
        self.base_url = base_url
        self.model = model
    
    async def check_connection(self) -> bool:
        """Check if LM Studio is running and accessible."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/v1/models", timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False
    
    async def list_models(self) -> list[str]:
        """Get list of available models from LM Studio."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/v1/models", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    return [model["id"] for model in data.get("data", [])]
        except Exception:
            pass
        return []
    
    async def auto_detect_model(self) -> str | None:
        """Auto-detect the first available embedding model from LM Studio."""
        models = await self.list_models()
        # Prefer models with 'embedding' in the name
        for model_id in models:
            if 'embedding' in model_id.lower():
                return model_id
        # Fallback to first available model
        return models[0] if models else None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a list of texts using LM Studio.
        
        Returns list of embedding vectors.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/embeddings",
                json={
                    "model": self.model,
                    "input": texts
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract embeddings from response
            embeddings = [item["embedding"] for item in data["data"]]
            return embeddings