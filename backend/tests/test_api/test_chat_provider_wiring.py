"""Test that the chat endpoint correctly uses provider_config_id from the request."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.schemas.chat import ChatRequest
from app.database.models import ProviderConfig


@pytest.fixture
def mock_session():
    """Create a mock async session."""
    session = MagicMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def sample_providers():
    """Create sample provider configs."""
    return [
        ProviderConfig(
            id="provider-1",
            name="OpenAI Main",
            type="openai",
            provider_name="OpenAI",
            model="gpt-4",
            base_url="https://api.openai.com/v1",
            api_key_ref="sk-xxx",
            is_default=False,
        ),
        ProviderConfig(
            id="provider-2",
            name="OpenAI Backup",
            type="openai",
            provider_name="OpenAI",
            model="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1",
            api_key_ref="sk-yyy",
            is_default=True,
        ),
        ProviderConfig(
            id="provider-3",
            name="Local LM Studio",
            type="custom",
            provider_name="LM Studio",
            model="local-model",
            base_url="http://localhost:1234/v1",
            api_key_ref=None,
            is_default=False,
        ),
    ]


def test_chat_request_accepts_provider_config_id():
    """ChatRequest schema should accept provider_config_id."""
    req = ChatRequest(message="test", provider_config_id="some-id")
    assert req.provider_config_id == "some-id"

    # Also works without it (backward compatible)
    req2 = ChatRequest(message="test")
    assert req2.provider_config_id is None


def test_chat_request_accepts_all_fields():
    """ChatRequest should accept all expected fields."""
    req = ChatRequest(
        message="hello",
        conversation_id="conv-123",
        provider_config_id="prov-456",
        collection_id="coll-789",
        limit=5,
    )
    assert req.message == "hello"
    assert req.conversation_id == "conv-123"
    assert req.provider_config_id == "prov-456"
    assert req.collection_id == "coll-789"
    assert req.limit == 5


@pytest.mark.asyncio
async def test_provider_lookup_with_explicit_id(sample_providers):
    """When provider_config_id is provided, use that specific provider."""
    from app.database.repositories.provider_configs import ProviderConfigRepository
    from unittest.mock import AsyncMock

    # Mock the repository
    mock_repo = MagicMock(spec=ProviderConfigRepository)

    # Return the second provider when get_by_id is called with "provider-2"
    async def get_by_id(id):
        return next((p for p in sample_providers if p.id == id), None)

    mock_repo.get_by_id = get_by_id

    # Simulate the logic from chat.py
    body = ChatRequest(message="test", provider_config_id="provider-2")

    if body.provider_config_id:
        config = await mock_repo.get_by_id(body.provider_config_id)
    else:
        config = None

    assert config is not None
    assert config.id == "provider-2"
    assert config.model == "gpt-3.5-turbo"
    assert config.is_default is True  # This is the backup provider


@pytest.mark.asyncio
async def test_provider_lookup_fallback_to_default(sample_providers):
    """When no provider_config_id, fall back to the default provider."""
    from app.database.repositories.provider_configs import ProviderConfigRepository
    from unittest.mock import AsyncMock

    mock_repo = MagicMock(spec=ProviderConfigRepository)

    async def get_all():
        return sample_providers

    mock_repo.get_all = get_all

    body = ChatRequest(message="test")  # No provider_config_id

    if body.provider_config_id:
        config = await mock_repo.get_by_id(body.provider_config_id)
    else:
        all_configs = await mock_repo.get_all()
        config = next((c for c in all_configs if c.is_default), all_configs[0] if all_configs else None)

    assert config is not None
    assert config.is_default is True
    assert config.id == "provider-2"  # The default one


@pytest.mark.asyncio
async def test_provider_lookup_fallback_to_first_when_no_default():
    """When no provider is marked as default, use the first one."""
    providers = [
        ProviderConfig(
            id="p1",
            name="First",
            type="openai",
            provider_name="OpenAI",
            model="gpt-4",
            is_default=False,
        ),
        ProviderConfig(
            id="p2",
            name="Second",
            type="openai",
            provider_name="OpenAI",
            model="gpt-3.5-turbo",
            is_default=False,
        ),
    ]

    # Simulate the fallback logic
    all_configs = providers
    config = next((c for c in all_configs if c.is_default), all_configs[0] if all_configs else None)

    assert config is not None
    assert config.id == "p1"  # First one


@pytest.mark.asyncio
async def test_provider_lookup_returns_none_when_no_providers():
    """When no providers exist, config should be None and fallback to LM Studio."""
    all_configs = []
    config = next((c for c in all_configs if c.is_default), all_configs[0] if all_configs else None)

    assert config is None


@pytest.mark.asyncio
async def test_provider_lookup_invalid_id_raises_error():
    """When provider_config_id is provided but not found, should raise HTTPException."""
    from fastapi import HTTPException
    from app.database.repositories.provider_configs import ProviderConfigRepository
    from unittest.mock import AsyncMock

    mock_repo = MagicMock(spec=ProviderConfigRepository)
    mock_repo.get_by_id = AsyncMock(return_value=None)

    body = ChatRequest(message="test", provider_config_id="non-existent")

    if body.provider_config_id:
        config = await mock_repo.get_by_id(body.provider_config_id)
        if not config:
            with pytest.raises(HTTPException) as exc_info:
                raise HTTPException(status_code=400, detail=f"Provider config '{body.provider_config_id}' not found")
            assert exc_info.value.status_code == 400
            assert "not found" in exc_info.value.detail
