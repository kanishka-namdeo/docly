import pytest
from app.ingestion.chunker import HierarchicalChunker

def test_chunker_basic():
    chunker = HierarchicalChunker(chunk_size=512, chunk_overlap=50)
    text = "This is a test document. " * 100
    
    chunks = chunker.chunk(text)
    
    assert len(chunks) > 0
    assert all("text" in chunk for chunk in chunks)
    assert all("metadata" in chunk for chunk in chunks)

def test_chunker_preserves_context():
    chunker = HierarchicalChunker(chunk_size=100, chunk_overlap=20)
    text = "First paragraph. " * 10 + "\n\n" + "Second paragraph. " * 10
    
    chunks = chunker.chunk(text)
    
    # Each chunk should have parent context
    assert all("parent_context" in chunk["metadata"] for chunk in chunks)
