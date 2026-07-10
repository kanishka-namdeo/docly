import pytest
from app.database.session import get_db_session, init_db
from app.database.repositories.collections import CollectionRepository
from app.database.repositories.documents import DocumentRepository

@pytest.fixture
async def db_session():
    await init_db()
    async with get_db_session() as session:
        yield session

@pytest.mark.asyncio
async def test_collection_repository_create(db_session):
    repo = CollectionRepository(db_session)
    collection = await repo.create(name="Test", description="Test desc")
    
    assert collection.name == "Test"
    assert collection.description == "Test desc"
    assert collection.id is not None

@pytest.mark.asyncio
async def test_collection_repository_get_all(db_session):
    repo = CollectionRepository(db_session)
    await repo.create(name="Test 1", description="Desc 1")
    await repo.create(name="Test 2", description="Desc 2")
    
    collections = await repo.get_all()
    assert len(collections) == 2

@pytest.mark.asyncio
async def test_collection_repository_get_by_id(db_session):
    repo = CollectionRepository(db_session)
    created = await repo.create(name="Test", description="Test")
    
    retrieved = await repo.get_by_id(created.id)
    assert retrieved.id == created.id
    assert retrieved.name == "Test"

@pytest.mark.asyncio
async def test_collection_repository_update(db_session):
    repo = CollectionRepository(db_session)
    created = await repo.create(name="Test", description="Test")
    
    updated = await repo.update(created.id, name="Updated", description="Updated desc")
    assert updated.name == "Updated"
    assert updated.description == "Updated desc"

@pytest.mark.asyncio
async def test_collection_repository_delete(db_session):
    repo = CollectionRepository(db_session)
    created = await repo.create(name="Test", description="Test")
    
    await repo.delete(created.id)
    retrieved = await repo.get_by_id(created.id)
    assert retrieved is None
