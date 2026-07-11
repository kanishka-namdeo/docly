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
    
    async def update(self, id: str, **kwargs) -> ProviderConfig | None:
        config = await self.get_by_id(id)
        if not config:
            return None
        
        for key, value in kwargs.items():
            if value is not None and hasattr(config, key):
                setattr(config, key, value)
        
        await self.session.flush()
        return config
    
    async def set_default(self, id: str) -> ProviderConfig | None:
        # First, unset all defaults
        result = await self.session.execute(select(ProviderConfig))
        all_configs = result.scalars().all()
        for config in all_configs:
            config.is_default = False
        
        # Then set the specified one as default
        config = await self.get_by_id(id)
        if config:
            config.is_default = True
            await self.session.flush()
            return config
        return None
    
    async def delete(self, id: str):
        config = await self.get_by_id(id)
        if config:
            await self.session.delete(config)
            await self.session.flush()
