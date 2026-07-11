from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import UserPreference


class UserPreferenceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self) -> UserPreference:
        """Get user preferences, creating default if not exists"""
        result = await self.session.execute(select(UserPreference))
        prefs = result.scalar_one_or_none()
        
        if not prefs:
            prefs = UserPreference()
            self.session.add(prefs)
            await self.session.flush()
        
        return prefs
    
    async def update(self, **kwargs) -> UserPreference:
        """Update user preferences"""
        prefs = await self.get()
        
        for key, value in kwargs.items():
            if value is not None and hasattr(prefs, key):
                setattr(prefs, key, value)
        
        await self.session.flush()
        return prefs
