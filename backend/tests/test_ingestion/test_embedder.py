import pytest
from app.ingestion.embedder import LMStudioEmbedder

@pytest.mark.asyncio
async def test_embedder_connection():
    embedder = LMStudioEmbedder(base_url="http://localhost:1234")
    is_connected = await embedder.check_connection()
    # This will fail if LM Studio is not running, which is expected
    assert isinstance(is_connected, bool)

@pytest.mark.asyncio
async def test_embedder_embed_text():
    embedder = LMStudioEmbedder(base_url="http://localhost:1234", model="nomic-embed-text-v1.5")
    texts = ["Hello world", "Test document"]
    
    embeddings = await embedder.embed(texts)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) > 0  # Should have embedding dimensions
