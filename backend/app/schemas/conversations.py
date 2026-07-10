from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConversationCreate(BaseModel):
    title: str
    collection_id: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    title: str
    collection_id: Optional[str] = None
    summary: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    role: str
    content: str


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    citations: Optional[list] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
