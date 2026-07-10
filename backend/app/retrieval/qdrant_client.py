from qdrant_client import QdrantClient as QdrantClientLib
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.config import settings

class QdrantClient:
    def __init__(self, collection_name: str = "documents"):
        self.client = QdrantClientLib(path=str(settings.qdrant_path))
        self.collection_name = collection_name
    
    async def ensure_collection(self, vector_size: int = 384):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
    
    async def upsert(self, points: list[dict]):
        """Insert or update points in the collection."""
        point_structs = [
            PointStruct(
                id=p["id"],
                vector=p["vector"],
                payload=p["payload"]
            )
            for p in points
        ]
        self.client.upsert(
            collection_name=self.collection_name,
            points=point_structs
        )
    
    async def search(self, vector: list[float], limit: int = 10, filter_dict: dict = None) -> list[dict]:
        """Search for similar vectors."""
        query_filter = None
        if filter_dict:
            conditions = []
            for key, value in filter_dict.items():
                conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )
            query_filter = Filter(must=conditions)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
            query_filter=query_filter
        )
        
        return [
            {
                "id": r.id,
                "score": r.score,
                "payload": r.payload
            }
            for r in results
        ]
    
    async def delete(self, point_ids: list[str]):
        """Delete points by IDs."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=point_ids
        )
    
    async def delete_by_filter(self, filter_dict: dict):
        """Delete points by filter."""
        conditions = []
        for key, value in filter_dict.items():
            if isinstance(value, dict) and "match" in value:
                conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value["match"]["value"]))
                )
        
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(must=conditions)
        )
