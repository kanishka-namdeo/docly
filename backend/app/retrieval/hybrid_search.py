from typing import Any
from app.retrieval.qdrant_client import QdrantClient
from app.ingestion.embedder import LMStudioEmbedder

class HybridSearch:
    def __init__(self, qdrant: QdrantClient, embedder: LMStudioEmbedder):
        self.qdrant = qdrant
        self.embedder = embedder
    
    async def search(self, query: str, limit: int = 10, collection_id: str = None) -> list[dict[str, Any]]:
        """Search for documents matching the query."""
        query_embedding = await self.embedder.embed([query])
        query_vector = query_embedding[0]
        
        filter_dict = None
        if collection_id:
            filter_dict = {"collection_id": collection_id}
        
        results = await self.qdrant.search(
            vector=query_vector,
            limit=limit,
            filter_dict=filter_dict
        )
        
        formatted = []
        for r in results:
            formatted.append({
                "text": r["payload"]["text"],
                "score": r["score"],
                "file_path": r["payload"]["file_path"],
                "collection_id": r["payload"]["collection_id"],
                "document_id": r["payload"]["document_id"],
                "chunk_index": r["payload"]["chunk_index"],
                "parent_context": r["payload"].get("parent_context", "")
            })
        
        return formatted
