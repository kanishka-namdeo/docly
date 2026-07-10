from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Collection

class CollectionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, name: str, description: str = None) -> Collection:
        collection = Collection(name=name, description=description)
        self.session.add(collection)
        await self.session.flush()
        return collection
    
    async def get_all(self) -> list[Collection]:
        result = await self.session.execute(select(Collection))
        return result.scalars().all()
    
    async def get_by_id(self, id: str) -> Collection | None:
        result = await self.session.execute(select(Collection).where(Collection.id == id))
        return result.scalar_one_or_none()
    
    async def update(self, id: str, **kwargs) -> Collection:
        collection = await self.get_by_id(id)
        if not collection:
            raise ValueError(f"Collection {id} not found")
        for key, value in kwargs.items():
            setattr(collection, key, value)
        await self.session.flush()
        return collection
    
    async def delete(self, id: str):
        collection = await self.get_by_id(id)
        if collection:
            await self.session.delete(collection)
            await self.session.flush()
