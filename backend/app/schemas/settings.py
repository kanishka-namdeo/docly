from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProviderConfigCreate(BaseModel):
    name: str
    type: str
    provider_name: str
    model: str
    base_url: Optional[str] = None
    api_key_ref: Optional[str] = None


class ProviderConfigResponse(BaseModel):
    id: str
    name: str
    type: str
    provider_name: str
    model: str
    base_url: Optional[str] = None
    api_key_ref: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LMStudioStatusResponse(BaseModel):
    connected: bool
    url: str
    models: Optional[list[str]] = None
    error: Optional[str] = None
