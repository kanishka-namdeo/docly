from typing import AsyncGenerator

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.database.repositories.provider_configs import ProviderConfigRepository
from app.ingestion.embedder import LMStudioEmbedder
from pydantic import BaseModel


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_db_session() as session:
        yield session


router = APIRouter(prefix="/settings", tags=["settings"])

class ProviderConfigCreate(BaseModel):
    name: str
    type: str
    provider_name: str
    model: str
    base_url: str = None
    api_key: str = None

class ProviderConfigResponse(BaseModel):
    id: str
    name: str
    type: str
    provider_name: str
    model: str
    base_url: str = None

class LMStudioStatus(BaseModel):
    connected: bool
    url: str
    model: str = None

@router.get("/providers", response_model=list[ProviderConfigResponse])
async def list_providers(session: AsyncSession = Depends(get_session)):
    repo = ProviderConfigRepository(session)
    configs = await repo.get_all()
    return [
        ProviderConfigResponse(
            id=c.id, name=c.name, type=c.type,
            provider_name=c.provider_name, model=c.model, base_url=c.base_url
        )
        for c in configs
    ]

@router.post("/providers", response_model=ProviderConfigResponse)
async def create_provider(data: ProviderConfigCreate, session: AsyncSession = Depends(get_session)):
    repo = ProviderConfigRepository(session)
    config = await repo.create(
        name=data.name, type=data.type, provider_name=data.provider_name,
        model=data.model, base_url=data.base_url, api_key_ref="placeholder"
    )
    return ProviderConfigResponse(
        id=config.id, name=config.name, type=config.type,
        provider_name=config.provider_name, model=config.model, base_url=config.base_url
    )

@router.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str, session: AsyncSession = Depends(get_session)):
    repo = ProviderConfigRepository(session)
    await repo.delete(provider_id)
    return {"status": "deleted"}

@router.get("/lm-studio/status", response_model=LMStudioStatus)
async def check_lm_studio_status():
    from app.config import settings
    embedder = LMStudioEmbedder(base_url=settings.lm_studio_url)
    connected = await embedder.check_connection()
    return LMStudioStatus(
        connected=connected,
        url=settings.lm_studio_url,
        model=settings.embedding_model if connected else None
    )
