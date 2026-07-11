from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentResponse(BaseModel):
    id: str
    collection_id: str
    file_path: str
    file_type: str
    file_size: int
    status: str
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    indexed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    document_id: str
    file_name: str
    status: str
    message: str



class BatchUploadResult(BaseModel):
    file_name: str
    status: str
    document_id: Optional[str] = None
    message: Optional[str] = None