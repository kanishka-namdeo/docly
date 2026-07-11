# backend/app/api/routes/chat.py
from fastapi import APIRouter, HTTPException, Depends
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.database.repositories.conversations import ConversationRepository
from app.database.repositories.messages import MessageRepository
from app.database.repositories.provider_configs import ProviderConfigRepository
from app.schemas.chat import ChatRequest, ChatResponse, ChatCitation

router = APIRouter()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_db_session() as session:
        yield session


@router.post("/", response_model=ChatResponse)
async def send_chat_message(
    body: ChatRequest, session: AsyncSession = Depends(get_session)
):
    """Send a message through the agentic RAG pipeline.

    Creates a new conversation if conversation_id is not provided.
    Searches relevant documents, generates a response via LLM,
    and returns the answer with citations.
    """
    conv_repo = ConversationRepository(session)
    msg_repo = MessageRepository(session)

    # Use existing or create a new conversation
    if body.conversation_id:
        conversation = await conv_repo.get_by_id(body.conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Auto-create conversation from first message
        title = body.message[:100] + ("..." if len(body.message) > 100 else "")
        conversation = await conv_repo.create(
            title=title, collection_id=body.collection_id
        )

    # Save user message
    user_msg = await msg_repo.create(
        conversation_id=conversation.id,
        role="user",
        content=body.message,
    )

    # Get conversation history for agentic RAG
    history_messages = await msg_repo.get_by_conversation(conversation.id, limit=10)
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in history_messages
        if msg.id != user_msg.id  # Exclude the message we just created
    ]

    # Get LLM provider config
    provider_repo = ProviderConfigRepository(session)

    if body.provider_config_id:
        # Use the provider explicitly selected by the frontend
        config = await provider_repo.get_by_id(body.provider_config_id)
        if not config:
            raise HTTPException(status_code=400, detail=f"Provider config '{body.provider_config_id}' not found")
    else:
        # Fall back to the default provider, or the first one if no default is set
        all_configs = await provider_repo.get_all()
        config = next((c for c in all_configs if c.is_default), all_configs[0] if all_configs else None)

    if config:
        provider_dict = {
            "type": config.type,
            "api_key": config.api_key_ref,
            "model": config.model,
            "base_url": config.base_url,
        }
    else:
        from app.config import settings
        provider_dict = {
            "type": "custom",
            "base_url": settings.lm_studio_url,
            "api_key": None,
            "model": "default",
        }

    # Initialize agentic RAG pipeline
    try:
        from app.llm.client import LLMClient
        from app.retrieval.hybrid_search import HybridSearch
        from app.retrieval.qdrant_client import QdrantClient
        from app.ingestion.embedder import LMStudioEmbedder
        from app.agentic.controller import AgenticController

        llm_client = LLMClient(provider_dict)
        embedder = LMStudioEmbedder()
        qdrant = QdrantClient()
        hybrid_search = HybridSearch(qdrant=qdrant, embedder=embedder)
        controller = AgenticController(llm=llm_client, search=hybrid_search)

        # Process through agentic RAG
        result = await controller.process(
            query=body.message,
            collection_id=body.collection_id,
            conversation_history=conversation_history,
        )

        response_text = result["answer"]
        reasoning = result.get("reasoning", "")
        iterations = result.get("iterations", 0)

        # Convert citations
        citations = []
        for citation_data in result.get("citations", []):
            citations.append(ChatCitation(
                text=citation_data.get("text", ""),
                score=citation_data.get("score", 0.0),
                file_path=citation_data.get("file_path", ""),
                collection_id=citation_data.get("collection_id"),
                document_id=citation_data.get("document_id"),
            ))
    except Exception as e:
        # Fallback to simple RAG if agentic pipeline fails
        import traceback
        error_detail = traceback.format_exc()
        response_text = f"Error in agentic RAG pipeline: {str(e)}"
        reasoning = f"Agentic pipeline failed, falling back to simple response.\n\nError details:\n{error_detail}"
        citations = []
        iterations = 0

    # Save assistant response with reasoning
    assistant_message = await msg_repo.create(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        citations=[c.model_dump() for c in citations],
        reasoning=reasoning,
    )

    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        content=response_text,
        citations=citations,
        reasoning=reasoning,
        iterations=iterations,
    )

