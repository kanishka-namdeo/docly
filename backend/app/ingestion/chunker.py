import re
from typing import Any

class HierarchicalChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(self, text: str, metadata: dict = None) -> list[dict[str, Any]]:
        """
        Split text into hierarchical chunks with parent context.
        
        Returns list of chunks, each with:
        - text: str
        - metadata: dict (includes parent_context)
        """
        # Split into paragraphs first
        paragraphs = re.split(r"\n\n+", text.strip())
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para.split())
            
            if current_size + para_size > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "parent_context": chunk_text,
                        "chunk_index": len(chunks),
                        **(metadata or {})
                    }
                })
                
                # Keep overlap
                overlap_words = []
                overlap_size = 0
                for word in reversed(current_chunk):
                    if overlap_size + len(word.split()) > self.chunk_overlap:
                        break
                    overlap_words.insert(0, word)
                    overlap_size += len(word.split())
                
                current_chunk = overlap_words
                current_size = overlap_size
            
            current_chunk.append(para)
            current_size += para_size
        
        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "parent_context": chunk_text,
                    "chunk_index": len(chunks),
                    **(metadata or {})
                }
            })
        
        return chunks
