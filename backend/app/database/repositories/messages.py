from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Message

class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, conversation_id: str, role: str, content: str, citations: list = None) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            citations=citations or []
        )
        self.session.add(message)
        await self.session.flush()
        return message
    
    async def get_by_conversation(self, conversation_id: str, limit: int = None) -> list[Message]:
        query = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
        if limit:
            query = query.limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_recent(self, conversation_id: str, count: int = 10) -> list[Message]:
        # Get all messages, then take last N
        all_messages = await self.get_by_conversation(conversation_id)
        return all_messages[-count:] if len(all_messages) > count else all_messages
