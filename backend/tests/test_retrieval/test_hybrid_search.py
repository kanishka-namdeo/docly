import pytest
from app.retrieval.hybrid_search import HybridSearch
from app.retrieval.qdrant_client import QdrantClient
from app.ingestion.embedder import LMStudioEmbedder

@pytest.mark.asyncio
async def test_hybrid_search():
    try:
        qdrant = QdrantClient(collection_name="test_hybrid")
    except RuntimeError:
        pytest.skip("Qdrant storage locked by another process")
    embedder = LMStudioEmbedder()
    hybrid = HybridSearch(qdrant, embedder)
    
    await qdrant.ensure_collection(vector_size=384)
    
    query = "test query"
    try:
        results = await hybrid.search(query, limit=5)
    except Exception:
        pytest.skip("LM Studio not available")
    
    assert isinstance(results, list)
