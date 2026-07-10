import pytest
from datetime import datetime
from sqlalchemy import select
from app.database.session import get_db_session, init_db
from app.database.models import Collection, Document, Conversation, Message, ProviderConfig

@pytest.fixture
async def db_session():
    await init_db()
    async with get_db_session() as session:
        yield session

@pytest.mark.asyncio
async def test_create_collection(db_session):
    collection = Collection(
        name="Test Collection",
        description="Test description"
    )
    db_session.add(collection)
    await db_session.commit()
    
    result = await db_session.execute(select(Collection))
    collections = result.scalars().all()
    assert len(collections) == 1
    assert collections[0].name == "Test Collection"

@pytest.mark.asyncio
async def test_create_document(db_session):
    collection = Collection(name="Test", description="Test")
    db_session.add(collection)
    await db_session.flush()
    
    document = Document(
        collection_id=collection.id,
        file_path="/test/file.pdf",
        file_type="pdf",
        file_size=1024,
        status="pending"
    )
    db_session.add(document)
    await db_session.commit()
    
    result = await db_session.execute(select(Document))
    documents = result.scalars().all()
    assert len(documents) == 1
    assert documents[0].file_type == "pdf"
    assert documents[0].status == "pending"

@pytest.mark.asyncio
async def test_create_conversation(db_session):
    conversation = Conversation(
        title="Test Conversation",
        collection_id=None
    )
    db_session.add(conversation)
    await db_session.commit()
    
    result = await db_session.execute(select(Conversation))
    conversations = result.scalars().all()
    assert len(conversations) == 1
    assert conversations[0].title == "Test Conversation"

@pytest.mark.asyncio
async def test_create_message(db_session):
    conversation = Conversation(title="Test", collection_id=None)
    db_session.add(conversation)
    await db_session.flush()
    
    message = Message(
        conversation_id=conversation.id,
        role="user",
        content="Hello",
        citations=[]
    )
    db_session.add(message)
    await db_session.commit()
    
    result = await db_session.execute(select(Message))
    messages = result.scalars().all()
    assert len(messages) == 1
    assert messages[0].role == "user"
    assert messages[0].content == "Hello"

@pytest.mark.asyncio
async def test_create_provider_config(db_session):
    config = ProviderConfig(
        name="Test Provider",
        type="builtin",
        provider_name="openai",
        model="gpt-4o",
        api_key_ref="test-key-ref"
    )
    db_session.add(config)
    await db_session.commit()
    
    result = await db_session.execute(select(ProviderConfig))
    configs = result.scalars().all()
    assert len(configs) == 1
    assert configs[0].provider_name == "openai"
