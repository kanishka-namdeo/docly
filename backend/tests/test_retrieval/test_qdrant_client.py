import uuid
import pytest
from app.retrieval.qdrant_client import QdrantClient

@pytest.mark.asyncio
async def test_qdrant_client_init():
    try:
        client = QdrantClient()
        assert client is not None
    except RuntimeError:
        pytest.skip("Qdrant storage locked by another process")

@pytest.mark.asyncio
async def test_qdrant_client_upsert_and_search():
    try:
        client = QdrantClient(collection_name="test_collection")
    except RuntimeError:
        pytest.skip("Qdrant storage locked by another process")
    
    await client.ensure_collection(vector_size=384)
    
    id1 = str(uuid.uuid4())
    id2 = str(uuid.uuid4())
    points = [
        {
            "id": id1,
            "vector": [0.1] * 384,
            "payload": {"text": "Test document 1", "collection_id": "test"}
        },
        {
            "id": id2,
            "vector": [0.2] * 384,
            "payload": {"text": "Test document 2", "collection_id": "test"}
        }
    ]
    await client.upsert(points)
    
    results = await client.search([0.1] * 384, limit=2)
    assert len(results) > 0

@pytest.mark.asyncio
async def test_qdrant_client_delete():
    try:
        client = QdrantClient(collection_name="test_collection_delete")
    except RuntimeError:
        pytest.skip("Qdrant storage locked by another process")
    
    await client.ensure_collection(vector_size=384)
    
    id1 = str(uuid.uuid4())
    id2 = str(uuid.uuid4())
    points = [
        {
            "id": id1,
            "vector": [0.1] * 384,
            "payload": {"text": "Test document 1", "collection_id": "test"}
        },
        {
            "id": id2,
            "vector": [0.2] * 384,
            "payload": {"text": "Test document 2", "collection_id": "test"}
        }
    ]
    await client.upsert(points)
    
    # Verify points exist
    results = await client.search([0.1] * 384, limit=10)
    assert len(results) == 2
    
    # Delete them
    await client.delete([id1, id2])
    
    results = await client.search([0.1] * 384, limit=10)
    assert len(results) == 0
