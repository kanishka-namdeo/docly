import pytest
from pathlib import Path
from app.ingestion.indexer import DocumentIndexer
from app.ingestion.embedder import LMStudioEmbedder
from app.retrieval.qdrant_client import QdrantClient

@pytest.mark.asyncio
async def test_indexer_pipeline():
    embedder = LMStudioEmbedder()
    qdrant = QdrantClient()
    indexer = DocumentIndexer(embedder, qdrant)
    
    # Create a test markdown file
    test_file = Path("/tmp/test_doc.md")
    test_file.write_text("# Test\n\nThis is a test document.")
    
    result = await indexer.index_file(str(test_file), collection_id="test-collection")
    
    assert result["status"] == "success"
    assert result["chunks_indexed"] > 0
    
    # Cleanup
    test_file.unlink()
