from typing import AsyncGenerator, Optional

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
    base_url: Optional[str] = None
    is_default: bool = False


class LMStudioStatus(BaseModel):
    connected: bool
    url: str
    model: Optional[str] = None
    models: Optional[list[str]] = None
    error: Optional[str] = None

class TestConnectionResponse(BaseModel):
    success: bool
    error: Optional[str] = None

class UserPreferenceResponse(BaseModel):
    theme: str
    language: str

class UserPreferenceUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None

@router.get("/providers", response_model=list[ProviderConfigResponse])
async def list_providers(session: AsyncSession = Depends(get_session)):
    repo = ProviderConfigRepository(session)
    configs = await repo.get_all()
    return [
        ProviderConfigResponse(
            id=c.id, name=c.name, type=c.type,
            provider_name=c.provider_name, model=c.model, base_url=c.base_url,
            is_default=c.is_default
        )
        for c in configs
    ]

@router.post("/providers", response_model=ProviderConfigResponse)
async def create_provider(data: ProviderConfigCreate, session: AsyncSession = Depends(get_session)):
    repo = ProviderConfigRepository(session)
    config = await repo.create(
        name=data.name, type=data.type, provider_name=data.provider_name,
        model=data.model, base_url=data.base_url, api_key_ref=data.api_key
    )
    return ProviderConfigResponse(
        id=config.id, name=config.name, type=config.type,
        provider_name=config.provider_name, model=config.model, base_url=config.base_url,
        is_default=config.is_default
    )

@router.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str, session: AsyncSession = Depends(get_session)):
    repo = ProviderConfigRepository(session)
    await repo.delete(provider_id)
    return {"status": "deleted"}

@router.put("/providers/{provider_id}", response_model=ProviderConfigResponse)
async def update_provider(provider_id: str, data: ProviderConfigUpdate, session: AsyncSession = Depends(get_session)):
    repo = ProviderConfigRepository(session)
    
    # Build update dict, only including non-None fields
    update_data = data.model_dump(exclude_none=True)
    
    # Handle api_key -> api_key_ref mapping
    if 'api_key' in update_data:
        update_data['api_key_ref'] = update_data.pop('api_key')
    
    if not update_data:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No fields to update")
    
    config = await repo.update(provider_id, **update_data)
    if not config:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return ProviderConfigResponse(
        id=config.id, name=config.name, type=config.type,
        provider_name=config.provider_name, model=config.model, base_url=config.base_url,
        is_default=config.is_default
    )


@router.post("/providers/test", response_model=TestConnectionResponse)
async def test_provider_connection(data: ProviderConfigCreate):
    """Test provider connection without saving to database"""
    try:
        if data.type == "builtin":
            if data.provider_name == "anthropic":
                import anthropic
                client = anthropic.Anthropic(api_key=data.api_key)
                # Simple test call
                client.models.list()
            elif data.provider_name == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=data.api_key)
                client.models.list()
            elif data.provider_name == "google":
                import google.generativeai as genai
                genai.configure(api_key=data.api_key)
                # List models as a test
                list(genai.list_models())
            else:
                return TestConnectionResponse(success=False, error=f"Unknown provider: {data.provider_name}")
        else:
            # Custom OpenAI-compatible endpoint
            from openai import OpenAI
            client = OpenAI(api_key=data.api_key or "dummy", base_url=data.base_url)
            client.models.list()
        
        return TestConnectionResponse(success=True, error=None)
    except Exception as e:
        return TestConnectionResponse(success=False, error=str(e))

@router.put("/providers/{provider_id}/default")
async def set_default_provider(provider_id: str, session: AsyncSession = Depends(get_session)):
    repo = ProviderConfigRepository(session)
    config = await repo.set_default(provider_id)
    if not config:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"status": "ok", "id": config.id, "is_default": config.is_default}

@router.get("/lm-studio/status", response_model=LMStudioStatus)
async def check_lm_studio_status():
    from app.config import settings
    embedder = LMStudioEmbedder(base_url=settings.lm_studio_url, model=settings.embedding_model)
    connected = await embedder.check_connection()
    
    models = None
    current_model = None
    error = None
    
    if connected:
        models = await embedder.list_models()
        # Use the configured model if it's available, otherwise use the first embedding model
        if settings.embedding_model in models:
            current_model = settings.embedding_model
        else:
            # Auto-detect an embedding model
            current_model = await embedder.auto_detect_model()
    else:
        error = "LM Studio is not running or not accessible"
    
    return LMStudioStatus(
        connected=connected,
        url=settings.lm_studio_url,
        model=current_model,
        models=models,
        error=error
    )


@router.get("/preferences", response_model=UserPreferenceResponse)
async def get_preferences(session: AsyncSession = Depends(get_session)):
    from app.database.repositories.user_preferences import UserPreferenceRepository
    repo = UserPreferenceRepository(session)
    prefs = await repo.get()
    return UserPreferenceResponse(theme=prefs.theme, language=prefs.language)

@router.put("/preferences", response_model=UserPreferenceResponse)
async def update_preferences(data: UserPreferenceUpdate, session: AsyncSession = Depends(get_session)):
    from app.database.repositories.user_preferences import UserPreferenceRepository
    repo = UserPreferenceRepository(session)
    
    update_data = data.model_dump(exclude_none=True)
    if not update_data:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No fields to update")
    
    prefs = await repo.update(**update_data)
    return UserPreferenceResponse(theme=prefs.theme, language=prefs.language)
class EmbeddingModelUpdate(BaseModel):
    model: str

@router.post("/embedding/model")
async def set_embedding_model(data: EmbeddingModelUpdate):
    from app.config import settings
    settings.set_embedding_model(data.model)
    return {"status": "ok", "model": data.model}

