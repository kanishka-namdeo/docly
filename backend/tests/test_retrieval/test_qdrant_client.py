import pytest
from app.retrieval.qdrant_client import QdrantClient

@pytest.mark.asyncio
async def test_qdrant_client_init():
    client = QdrantClient()
    assert client is not None

@pytest.mark.asyncio
async def test_qdrant_client_upsert_and_search():
    client = QdrantClient(collection_name="test_collection")
    
    await client.ensure_collection(vector_size=384)
    
    points = [
        {
            "id": "test_1",
            "vector": [0.1] * 384,
            "payload": {"text": "Test document 1", "collection_id": "test"}
        },
        {
            "id": "test_2",
            "vector": [0.2] * 384,
            "payload": {"text": "Test document 2", "collection_id": "test"}
        }
    ]
    await client.upsert(points)
    
    results = await client.search([0.1] * 384, limit=2)
    assert len(results) > 0

@pytest.mark.asyncio
async def test_qdrant_client_delete():
    client = QdrantClient(collection_name="test_collection")
    await client.delete(["test_1", "test_2"])
    
    results = await client.search([0.1] * 384, limit=10)
    assert len(results) == 0
