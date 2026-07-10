from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Conversation

class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, title: str, collection_id: str = None) -> Conversation:
        conversation = Conversation(title=title, collection_id=collection_id)
        self.session.add(conversation)
        await self.session.flush()
        return conversation
    
    async def get_all(self) -> list[Conversation]:
        result = await self.session.execute(select(Conversation))
        return result.scalars().all()
    
    async def get_by_id(self, id: str) -> Conversation | None:
        result = await self.session.execute(select(Conversation).where(Conversation.id == id))
        return result.scalar_one_or_none()
    
    async def update(self, id: str, **kwargs) -> Conversation:
        conversation = await self.get_by_id(id)
        if not conversation:
            raise ValueError(f"Conversation {id} not found")
        for key, value in kwargs.items():
            setattr(conversation, key, value)
        await self.session.flush()
        return conversation
    
    async def delete(self, id: str):
        conversation = await self.get_by_id(id)
        if conversation:
            await self.session.delete(conversation)
            await self.session.flush()
