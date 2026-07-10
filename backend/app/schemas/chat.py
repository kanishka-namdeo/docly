from pydantic import BaseModel
from typing import Optional


class ChatCitation(BaseModel):
    text: str
    score: float
    file_path: str
    collection_id: Optional[str] = None
    document_id: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    collection_id: Optional[str] = None
    limit: int = 10


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    content: str
    citations: list[ChatCitation] = []
