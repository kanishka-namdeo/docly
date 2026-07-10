import pytest
from app.retrieval.hybrid_search import HybridSearch
from app.retrieval.qdrant_client import QdrantClient
from app.ingestion.embedder import LMStudioEmbedder

@pytest.mark.asyncio
async def test_hybrid_search():
    qdrant = QdrantClient(collection_name="test_hybrid")
    embedder = LMStudioEmbedder()
    hybrid = HybridSearch(qdrant, embedder)
    
    await qdrant.ensure_collection(vector_size=384)
    
    query = "test query"
    results = await hybrid.search(query, limit=5)
    
    assert isinstance(results, list)
