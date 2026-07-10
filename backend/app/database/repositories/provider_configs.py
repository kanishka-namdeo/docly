from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import ProviderConfig

class ProviderConfigRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, name: str, type: str, provider_name: str, model: str, base_url: str = None, api_key_ref: str = None) -> ProviderConfig:
        config = ProviderConfig(
            name=name,
            type=type,
            provider_name=provider_name,
            model=model,
            base_url=base_url,
            api_key_ref=api_key_ref
        )
        self.session.add(config)
        await self.session.flush()
        return config
    
    async def get_all(self) -> list[ProviderConfig]:
        result = await self.session.execute(select(ProviderConfig))
        return result.scalars().all()
    
    async def get_by_id(self, id: str) -> ProviderConfig | None:
        result = await self.session.execute(select(ProviderConfig).where(ProviderConfig.id == id))
        return result.scalar_one_or_none()
    
    async def delete(self, id: str):
        config = await self.get_by_id(id)
        if config:
            await self.session.delete(config)
            await self.session.flush()
