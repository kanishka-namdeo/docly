import hashlib
from pathlib import Path
from datetime import datetime
from typing import Any

from app.ingestion.parsers.base import BaseParser
from app.ingestion.parsers.pdf import PDFParser
from app.ingestion.parsers.docx import DOCXParser
from app.ingestion.parsers.excel import ExcelParser
from app.ingestion.parsers.markdown import MarkdownParser
from app.ingestion.parsers.html import HTMLParser
from app.ingestion.chunker import HierarchicalChunker
from app.ingestion.embedder import LMStudioEmbedder
from app.retrieval.qdrant_client import QdrantClient

class DocumentIndexer:
    def __init__(self, embedder: LMStudioEmbedder, qdrant: QdrantClient):
        self.embedder = embedder
        self.qdrant = qdrant
        self.chunker = HierarchicalChunker(chunk_size=512, chunk_overlap=50)
        self.parsers = {
            ".pdf": PDFParser(),
            ".docx": DOCXParser(),
            ".xlsx": ExcelParser(),
            ".md": MarkdownParser(),
            ".html": HTMLParser(),
            ".htm": HTMLParser(),
        }
    
    def _get_parser(self, file_path: str) -> BaseParser:
        ext = Path(file_path).suffix.lower()
        parser = self.parsers.get(ext)
        if not parser:
            raise ValueError(f"Unsupported file type: {ext}")
        return parser
    
    def _generate_document_id(self, file_path: str) -> str:
        return hashlib.md5(file_path.encode()).hexdigest()
    
    async def index_file(self, file_path: str, collection_id: str) -> dict[str, Any]:
        """
        Index a single file: parse → chunk → embed → store.
        
        Returns dict with status and metadata.
        """
        try:
            parser = self._get_parser(file_path)
            with open(file_path, "rb") as f:
                content = f.read()
            parsed = parser.parse(content)
            
            chunks = self.chunker.chunk(parsed["text"], metadata={
                "file_path": file_path,
                "collection_id": collection_id,
                "document_id": self._generate_document_id(file_path)
            })
            
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = await self.embedder.embed(chunk_texts)
            
            points = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                points.append({
                    "id": f"{self._generate_document_id(file_path)}_{i}",
                    "vector": embedding,
                    "payload": {
                        "text": chunk["text"],
                        "file_path": file_path,
                        "collection_id": collection_id,
                        "document_id": self._generate_document_id(file_path),
                        "chunk_index": i,
                        "parent_context": chunk["metadata"].get("parent_context", ""),
                        "indexed_at": datetime.utcnow().isoformat()
                    }
                })
            
            await self.qdrant.upsert(points)
            
            return {
                "status": "success",
                "chunks_indexed": len(chunks),
                "document_id": self._generate_document_id(file_path)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def remove_document(self, file_path: str):
        """Remove all chunks for a document from the index."""
        document_id = self._generate_document_id(file_path)
        await self.qdrant.delete_by_filter({
            "must": [{"key": "document_id", "match": {"value": document_id}}]
        })
