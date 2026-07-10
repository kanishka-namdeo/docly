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
    await msg_repo.create(
        conversation_id=conversation.id,
        role="user",
        content=body.message,
    )

    # RAG retrieval
    citations = []
    context_text = ""

    try:
        from app.retrieval.hybrid_search import HybridSearch
        from app.retrieval.qdrant_client import QdrantClient
        from app.ingestion.embedder import LMStudioEmbedder

        embedder = LMStudioEmbedder()
        qdrant = QdrantClient()
        hybrid_search = HybridSearch(qdrant=qdrant, embedder=embedder)

        search_results = await hybrid_search.search(
            body.message,
            limit=body.limit,
            collection_id=body.collection_id,
        )

        for r in search_results:
            citations.append(
                ChatCitation(
                    text=r["text"],
                    score=r["score"],
                    file_path=r["file_path"],
                    collection_id=r.get("collection_id"),
                    document_id=r.get("document_id"),
                )
            )
            context_text += f"\n---\n{r['text']}"

    except Exception:
        pass  # Graceful fallback: no context if search fails

    # Build messages for LLM
    system_prompt = (
        "You are a helpful document assistant. Answer questions based on the "
        "provided context. If the context doesn't contain relevant information, "
        "say so honestly. Cite sources when possible."
    )

    messages = [{"role": "system", "content": system_prompt}]

    if context_text:
        messages.append(
            {
                "role": "system",
                "content": f"Context documents:\n{context_text}",
            }
        )

    messages.append({"role": "user", "content": body.message})

    # Get LLM provider config
    provider_repo = ProviderConfigRepository(session)
    provider_configs = await provider_repo.get_all()

    if provider_configs:
        # Use the first configured provider
        config = provider_configs[0]
        provider_dict = {
            "type": config.type,
            "api_key": config.api_key_ref,
            "model": config.model,
            "base_url": config.base_url,
        }
    else:
        # Default to custom (LM Studio) if no provider configured
        from app.config import settings

        provider_dict = {
            "type": "custom",
            "base_url": settings.lm_studio_url,
            "api_key": None,
            "model": "default",
        }

    # Generate response
    try:
        from app.llm.client import LLMClient

        llm_client = LLMClient(provider_dict)
        response_text = await llm_client.chat(messages)
    except Exception as e:
        response_text = f"Error generating response: {str(e)}"

    # Save assistant response
    assistant_message = await msg_repo.create(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        citations=[c.model_dump() for c in citations],
    )

    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        content=response_text,
        citations=citations,
    )
