# backend/app/api/routes/conversations.py
from fastapi import APIRouter, HTTPException, Depends
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.database.repositories.conversations import ConversationRepository
from app.database.repositories.messages import MessageRepository
from app.schemas.conversations import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)

router = APIRouter()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_db_session() as session:
        yield session


@router.get("/", response_model=list[ConversationResponse])
async def list_conversations(session: AsyncSession = Depends(get_session)):
    repo = ConversationRepository(session)
    conversations = await repo.get_all()
    return conversations


@router.post("/", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    body: ConversationCreate, session: AsyncSession = Depends(get_session)
):
    repo = ConversationRepository(session)
    conversation = await repo.create(
        title=body.title, collection_id=body.collection_id
    )
    return conversation


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str, session: AsyncSession = Depends(get_session)
):
    repo = ConversationRepository(session)
    conversation = await repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    body: ConversationUpdate,
    session: AsyncSession = Depends(get_session)
):
    repo = ConversationRepository(session)
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    conversation = await repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conversation = await repo.update(conversation_id, **update_data)
    return conversation


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str, session: AsyncSession = Depends(get_session)
):
    repo = ConversationRepository(session)
    conversation = await repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await repo.delete(conversation_id)
    return None


# --- Messages sub-routes ---

@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    limit: int | None = None,
    session: AsyncSession = Depends(get_session),
):
    """Get messages for a conversation, optionally limited."""
    conv_repo = ConversationRepository(session)
    conversation = await conv_repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_repo = MessageRepository(session)
    messages = await msg_repo.get_by_conversation(conversation_id, limit=limit)
    return messages


@router.post(
    "/{conversation_id}/messages", response_model=MessageResponse, status_code=201
)
async def add_message(
    conversation_id: str,
    body: MessageCreate,
    session: AsyncSession = Depends(get_session),
):
    """Add a message to an existing conversation."""
    conv_repo = ConversationRepository(session)
    conversation = await conv_repo.get_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_repo = MessageRepository(session)
    message = await msg_repo.create(
        conversation_id=conversation_id,
        role=body.role,
        content=body.content,
    )
    return message
