from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Document

class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, collection_id: str, file_path: str, file_type: str, file_size: int) -> Document:
        document = Document(
            collection_id=collection_id,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            status="pending"
        )
        self.session.add(document)
        await self.session.flush()
        return document
    
    async def get_by_id(self, id: str) -> Document | None:
        result = await self.session.execute(select(Document).where(Document.id == id))
        return result.scalar_one_or_none()
    
    async def get_by_collection(self, collection_id: str) -> list[Document]:
        result = await self.session.execute(
            select(Document).where(Document.collection_id == collection_id)
        )
        return result.scalars().all()
    
    async def get_by_path(self, file_path: str) -> Document | None:
        result = await self.session.execute(
            select(Document).where(Document.file_path == file_path)
        )
        return result.scalar_one_or_none()
    
    async def update_status(self, id: str, status: str, error_message: str = None):
        document = await self.get_by_id(id)
        if document:
            document.status = status
            document.error_message = error_message
            if status == "indexed":
                from datetime import datetime
                document.indexed_at = datetime.utcnow()
            await self.session.flush()
    
    async def delete(self, id: str):
        document = await self.get_by_id(id)
        if document:
            await self.session.delete(document)
            await self.session.flush()
