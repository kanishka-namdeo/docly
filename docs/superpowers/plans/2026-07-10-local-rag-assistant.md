# Local RAG Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-first desktop RAG assistant with agentic retrieval that enables users to chat with their documents using cloud LLMs.

**Architecture:** Tauri 2.x desktop app with React frontend and Python FastAPI sidecar. Agentic RAG pipeline uses Qdrant embedded for hybrid search, LM Studio for embeddings, and cloud LLM APIs for reasoning. Documents are auto-indexed with type-aware parsing and hierarchical chunking.

**Tech Stack:** Tauri 2.x, React 18, Python 3.11+, FastAPI, Qdrant-client, sentence-transformers, LM Studio, Unstructured.io, LangGraph, Arize Phoenix, Ragas, GPTCache, tenacity

---

## File Structure

### Backend (Python FastAPI)
```
backend/
  app/
    __init__.py
    main.py                          # FastAPI app entry point
    config.py                        # Settings, env vars, paths
    database/
      __init__.py
      models.py                      # SQLAlchemy models
      session.py                     # DB connection, migrations
      repositories/
        __init__.py
        collections.py               # Collection CRUD
        documents.py                 # Document CRUD
        conversations.py             # Conversation CRUD
        messages.py                  # Message CRUD
        provider_configs.py          # Provider config CRUD
    ingestion/
      __init__.py
      parsers/
        __init__.py
        base.py                      # Base parser interface
        pdf.py                       # PDF parser (Unstructured)
        docx.py                      # DOCX parser (Unstructured)
        excel.py                     # Excel parser (Unstructured)
        markdown.py                  # Markdown parser
        html.py                      # HTML parser (Unstructured)
      chunker.py                     # Hierarchical chunking logic
      embedder.py                    # LM Studio embedding client
      indexer.py                     # Orchestrate parse → chunk → embed → index
      watcher.py                     # File system auto-watch
    retrieval/
      __init__.py
      qdrant_client.py               # Qdrant embedded client wrapper
      hybrid_search.py               # BM25 + vector + RRF
      reranker.py                    # Reranking logic (Qdrant RRF)
    agentic/
      __init__.py
      planner.py                     # Query decomposition
      evaluator.py                   # Retrieval confidence scoring
      critic.py                      # Answer validation against sources
      controller.py                  # Iteration loop orchestration
    llm/
      __init__.py
      providers/
        __init__.py
        base.py                      # Base provider interface
        anthropic.py                 # Claude provider
        openai.py                    # OpenAI provider
        google.py                    # Gemini provider
        custom.py                    # Custom OpenAI-compatible provider
      client.py                      # Unified LLM client
    cache/
      __init__.py
      gpt_cache.py                   # GPTCache semantic cache wrapper
    tracing/
      __init__.py
      phoenix.py                     # Arize Phoenix embedded setup
    evaluation/
      __init__.py
      ragas_eval.py                  # Ragas evaluation runner
    api/
      __init__.py
      routes/
        __init__.py
        collections.py               # Collection endpoints
        documents.py                 # Document endpoints
        conversations.py             # Conversation endpoints
        messages.py                  # Message endpoints
        settings.py                  # Settings endpoints
        chat.py                      # Chat/query endpoint
  tests/
    __init__.py
    test_ingestion/
      __init__.py
      test_parsers.py
      test_chunker.py
      test_embedder.py
      test_indexer.py
    test_retrieval/
      __init__.py
      test_qdrant_client.py
      test_hybrid_search.py
    test_agentic/
      __init__.py
      test_planner.py
      test_evaluator.py
      test_critic.py
      test_controller.py
    test_llm/
      __init__.py
      test_providers.py
      test_client.py
    test_api/
      __init__.py
      test_collections.py
      test_documents.py
      test_conversations.py
      test_chat.py
  requirements.txt
  pyproject.toml
```

### Frontend (React)
```
frontend/
  src/
    components/
      Chat/
        ChatWindow.tsx
        MessageList.tsx
        MessageInput.tsx
        CitationCard.tsx
      Documents/
        CollectionList.tsx
        DocumentList.tsx
        DocumentStatus.tsx
      Settings/
        ModelConfig.tsx
        EmbeddingConfig.tsx
        ApiKeyInput.tsx
      Layout/
        Sidebar.tsx
        Header.tsx
    pages/
      Chat.tsx
      Documents.tsx
      Settings.tsx
    hooks/
      useConversations.ts
      useCollections.ts
      useMessages.ts
    services/
      api.ts                         # Tauri IPC calls to backend
    types/
      index.ts                       # TypeScript types
    App.tsx
    main.tsx
  package.json
  vite.config.ts
  tsconfig.json
```

### Tauri (Rust)
```
src-tauri/
  src/
    main.rs                          # Tauri entry point
    lib.rs                           # Tauri setup
    commands/
      mod.rs
      backend.rs                     # Python sidecar management
  Cargo.toml
  tauri.conf.json
  build.rs
```

---

## Phase 1: Foundation

### Task 1: Project Scaffolding

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`

- [ ] **Step 1: Create backend directory structure**

```bash
mkdir -p backend/app/database/repositories
mkdir -p backend/app/ingestion/parsers
mkdir -p backend/app/retrieval
mkdir -p backend/app/agentic
mkdir -p backend/app/llm/providers
mkdir -p backend/app/cache
mkdir -p backend/app/tracing
mkdir -p backend/app/evaluation
mkdir -p backend/app/api/routes
mkdir -p backend/tests/test_ingestion
mkdir -p backend/tests/test_retrieval
mkdir -p backend/tests/test_agentic
mkdir -p backend/tests/test_llm
mkdir -p backend/tests/test_api
```

- [ ] **Step 2: Create requirements.txt with dependencies**

```txt
# Core
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.2
pydantic-settings==2.5.2

# Database
sqlalchemy==2.0.35
aiosqlite==0.20.0

# Vector DB
qdrant-client==1.12.0

# Document Parsing
unstructured[all-docs]==0.15.12

# Embeddings
httpx==0.27.2

# LLM Providers
anthropic==0.37.1
openai==1.51.0
google-generativeai==0.8.3

# Agentic RAG
langgraph==0.2.38

# Production
tenacity==9.0.0
gptcache==0.1.27
arize-phoenix==5.6.0
ragas==0.2.3

# File Watching
watchdog==5.0.3

# Testing
pytest==8.3.3
pytest-asyncio==0.24.0
pytest-cov==5.0.0
httpx==0.27.2
```

- [ ] **Step 3: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "doc-assistant-backend"
version = "0.1.0"
description = "Local RAG assistant backend"
requires-python = ">=3.11"
dependencies = [
    "fastapi==0.115.0",
    "uvicorn[standard]==0.32.0",
    "pydantic==2.9.2",
    "pydantic-settings==2.5.2",
    "sqlalchemy==2.0.35",
    "aiosqlite==0.20.0",
    "qdrant-client==1.12.0",
    "unstructured[all-docs]==0.15.12",
    "httpx==0.27.2",
    "anthropic==0.37.1",
    "openai==1.51.0",
    "google-generativeai==0.8.3",
    "langgraph==0.2.38",
    "tenacity==9.0.0",
    "gptcache==0.1.27",
    "arize-phoenix==5.6.0",
    "ragas==0.2.3",
    "watchdog==5.0.3",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 4: Create config.py**

```python
# backend/app/config.py
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Paths
    data_dir: Path = Path.home() / ".doc-assistant"
    db_path: Path = data_dir / "app.db"
    qdrant_path: Path = data_dir / "qdrant"
    cache_path: Path = data_dir / "cache.db"
    
    # LM Studio
    lm_studio_url: str = "http://localhost:1234"
    embedding_model: str = "nomic-embed-text-v1.5"
    
    # Arize Phoenix
    phoenix_enabled: bool = True
    phoenix_port: int = 6006
    
    # API
    host: str = "127.0.0.1"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Ensure data directory exists
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.qdrant_path.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 5: Create main.py**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Doc Assistant Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

- [ ] **Step 6: Create __init__.py files**

```bash
touch backend/app/__init__.py
touch backend/app/database/__init__.py
touch backend/app/database/repositories/__init__.py
touch backend/app/ingestion/__init__.py
touch backend/app/ingestion/parsers/__init__.py
touch backend/app/retrieval/__init__.py
touch backend/app/agentic/__init__.py
touch backend/app/llm/__init__.py
touch backend/app/llm/providers/__init__.py
touch backend/app/cache/__init__.py
touch backend/app/tracing/__init__.py
touch backend/app/evaluation/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/routes/__init__.py
touch backend/tests/__init__.py
touch backend/tests/test_ingestion/__init__.py
touch backend/tests/test_retrieval/__init__.py
touch backend/tests/test_agentic/__init__.py
touch backend/tests/test_llm/__init__.py
touch backend/tests/test_api/__init__.py
```

- [ ] **Step 7: Test backend starts**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Expected: Server starts at http://127.0.0.1:8000, health check returns `{"status": "ok"}`

- [ ] **Step 8: Commit**

```bash
git add backend/
git commit -m "feat: add backend scaffolding with FastAPI"
```

---

### Task 2: Database Models and Session

**Files:**
- Create: `backend/app/database/models.py`
- Create: `backend/app/database/session.py`
- Test: `backend/tests/test_database/test_models.py`

- [ ] **Step 1: Write failing test for database models**

```python
# backend/tests/test_database/test_models.py
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_database/test_models.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'app.database.models'"

- [ ] **Step 3: Create database models**

```python
# backend/app/database/models.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    documents = relationship("Document", back_populates="collection", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collection_id = Column(String, ForeignKey("collections.id"), nullable=False)
    file_path = Column(Text, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    indexed_at = Column(DateTime, nullable=True)
    
    collection = relationship("Collection", back_populates="documents")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    collection_id = Column(String, ForeignKey("collections.id"), nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class ProviderConfig(Base):
    __tablename__ = "provider_configs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    provider_name = Column(String, nullable=False)
    base_url = Column(Text, nullable=True)
    model = Column(String, nullable=False)
    api_key_ref = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 4: Create database session**

```python
# backend/app/database/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from app.config import settings
from app.database.models import Base

engine = create_async_engine(
    f"sqlite+aiosqlite:///{settings.db_path}",
    echo=False,
    future=True
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def get_db_session():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd backend
pytest tests/test_database/test_models.py -v
```

Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add backend/
git commit -m "feat: add database models and session management"
```

---

### Task 3: Database Repositories

**Files:**
- Create: `backend/app/database/repositories/collections.py`
- Create: `backend/app/database/repositories/documents.py`
- Create: `backend/app/database/repositories/conversations.py`
- Create: `backend/app/database/repositories/messages.py`
- Create: `backend/app/database/repositories/provider_configs.py`
- Test: `backend/tests/test_database/test_repositories.py`

- [ ] **Step 1: Write failing test for collection repository**

```python
# backend/tests/test_database/test_repositories.py
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

```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_database/test_repositories.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Create collection repository**

```python
# backend/app/database/repositories/collections.py
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
```

- [ ] **Step 4: Create document repository**

```python
# backend/app/database/repositories/documents.py
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
```

- [ ] **Step 5: Create conversation repository**

```python
# backend/app/database/repositories/conversations.py
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
```

- [ ] **Step 6: Create message repository**

```python
# backend/app/database/repositories/messages.py
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
```

- [ ] **Step 7: Create provider config repository**

```python
# backend/app/database/repositories/provider_configs.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import ProviderConfig

class ProviderConfigRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, name: str, type: str, provider_name: str, model: str, base_url: str = None, api_key_ref: str = None) -> ProviderConfig:
        config = ProviderConfig(
            name=name,
            type=type,
            provider_name=provider_name,
            model=model,
            base_url=base_url,
            api_key_ref=api_key_ref
        )
        self.session.add(config)
        await self.session.flush()
        return config
    
    async def get_all(self) -> list[ProviderConfig]:
        result = await self.session.execute(select(ProviderConfig))
        return result.scalars().all()
    
    async def get_by_id(self, id: str) -> ProviderConfig | None:
        result = await self.session.execute(select(ProviderConfig).where(ProviderConfig.id == id))
        return result.scalar_one_or_none()
    
    async def delete(self, id: str):
        config = await self.get_by_id(id)
        if config:
            await self.session.delete(config)
            await self.session.flush()
```

- [ ] **Step 8: Run test to verify it passes**

```bash
cd backend
pytest tests/test_database/test_repositories.py -v
```

Expected: All tests PASS

- [ ] **Step 9: Commit**

```bash
git add backend/
git commit -m "feat: add database repositories for all models"
```

---

## Phase 2: Document Ingestion

### Task 4: Document Parsers

**Files:**
- Create: `backend/app/ingestion/parsers/base.py`
- Create: `backend/app/ingestion/parsers/pdf.py`
- Create: `backend/app/ingestion/parsers/docx.py`
- Create: `backend/app/ingestion/parsers/excel.py`
- Create: `backend/app/ingestion/parsers/markdown.py`
- Create: `backend/app/ingestion/parsers/html.py`
- Test: `backend/tests/test_ingestion/test_parsers.py`

- [ ] **Step 1: Write failing test for parsers**

```python
# backend/tests/test_ingestion/test_parsers.py
import pytest
from pathlib import Path
from app.ingestion.parsers.base import BaseParser
from app.ingestion.parsers.markdown import MarkdownParser

def test_markdown_parser_basic():
    parser = MarkdownParser()
    content = "# Title\n\nThis is a paragraph.\n\n## Section\n\nAnother paragraph."
    result = parser.parse(content)
    
    assert result["text"] is not None
    assert len(result["text"]) > 0
    assert "Title" in result["text"]
    assert "paragraph" in result["text"]

def test_markdown_parser_preserves_structure():
    parser = MarkdownParser()
    content = "# Main Title\n\nContent here.\n\n## Subsection\n\nMore content."
    result = parser.parse(content)
    
    assert result["metadata"]["has_headings"] is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_ingestion/test_parsers.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Create base parser interface**

```python
# backend/app/ingestion/parsers/base.py
from abc import ABC, abstractmethod
from typing import Any

class BaseParser(ABC):
    @abstractmethod
    def parse(self, content: str | bytes) -> dict[str, Any]:
        """
        Parse document content and return structured data.
        
        Returns:
            dict with keys:
            - text: str (extracted text)
            - metadata: dict (document metadata)
            - elements: list[dict] (structured elements like sections, tables)
        """
        pass
```

- [ ] **Step 4: Create markdown parser**

```python
# backend/app/ingestion/parsers/markdown.py
import re
from app.ingestion.parsers.base import BaseParser

class MarkdownParser(BaseParser):
    def parse(self, content: str | bytes) -> dict:
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        
        # Extract headings
        headings = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
        
        # Clean markdown syntax for text extraction
        text = content
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)  # Remove heading markers
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # Remove bold
        text = re.sub(r"\*(.+?)\*", r"\1", text)  # Remove italic
        text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)  # Remove links, keep text
        
        return {
            "text": text.strip(),
            "metadata": {
                "has_headings": len(headings) > 0,
                "heading_count": len(headings),
                "headings": headings
            },
            "elements": []
        }
```

- [ ] **Step 5: Create PDF parser using Unstructured**

```python
# backend/app/ingestion/parsers/pdf.py
from unstructured.partition.pdf import partition_pdf
from app.ingestion.parsers.base import BaseParser

class PDFParser(BaseParser):
    def parse(self, content: str | bytes) -> dict:
        if isinstance(content, str):
            # Assume it's a file path
            elements = partition_pdf(filename=content)
        else:
            # It's bytes content
            elements = partition_pdf(file=content)
        
        text = "\n\n".join([str(el) for el in elements])
        
        return {
            "text": text.strip(),
            "metadata": {
                "element_count": len(elements),
                "has_tables": any("Table" in str(type(el)) for el in elements)
            },
            "elements": [{"type": str(type(el).__name__), "text": str(el)} for el in elements]
        }
```

- [ ] **Step 6: Create DOCX parser**

```python
# backend/app/ingestion/parsers/docx.py
from unstructured.partition.docx import partition_docx
from app.ingestion.parsers.base import BaseParser

class DOCXParser(BaseParser):
    def parse(self, content: str | bytes) -> dict:
        if isinstance(content, str):
            elements = partition_docx(filename=content)
        else:
            elements = partition_docx(file=content)
        
        text = "\n\n".join([str(el) for el in elements])
        
        return {
            "text": text.strip(),
            "metadata": {
                "element_count": len(elements)
            },
            "elements": [{"type": str(type(el).__name__), "text": str(el)} for el in elements]
        }
```

- [ ] **Step 7: Create Excel parser**

```python
# backend/app/ingestion/parsers/excel.py
from unstructured.partition.xlsx import partition_xlsx
from app.ingestion.parsers.base import BaseParser

class ExcelParser(BaseParser):
    def parse(self, content: str | bytes) -> dict:
        if isinstance(content, str):
            elements = partition_xlsx(filename=content)
        else:
            elements = partition_xlsx(file=content)
        
        text = "\n\n".join([str(el) for el in elements])
        
        return {
            "text": text.strip(),
            "metadata": {
                "element_count": len(elements)
            },
            "elements": [{"type": str(type(el).__name__), "text": str(el)} for el in elements]
        }
```

- [ ] **Step 8: Create HTML parser**

```python
# backend/app/ingestion/parsers/html.py
from unstructured.partition.html import partition_html
from app.ingestion.parsers.base import BaseParser

class HTMLParser(BaseParser):
    def parse(self, content: str | bytes) -> dict:
        if isinstance(content, str):
            elements = partition_html(text=content)
        else:
            elements = partition_html(file=content)
        
        text = "\n\n".join([str(el) for el in elements])
        
        return {
            "text": text.strip(),
            "metadata": {
                "element_count": len(elements)
            },
            "elements": [{"type": str(type(el).__name__), "text": str(el)} for el in elements]
        }
```

- [ ] **Step 9: Run test to verify it passes**

```bash
cd backend
pytest tests/test_ingestion/test_parsers.py -v
```

Expected: All tests PASS

- [ ] **Step 10: Commit**

```bash
git add backend/
git commit -m "feat: add document parsers for PDF, DOCX, Excel, Markdown, HTML"
```

---

### Task 5: Hierarchical Chunker

**Files:**
- Create: `backend/app/ingestion/chunker.py`
- Test: `backend/tests/test_ingestion/test_chunker.py`

- [ ] **Step 1: Write failing test for chunker**

```python
# backend/tests/test_ingestion/test_chunker.py
import pytest
from app.ingestion.chunker import HierarchicalChunker

def test_chunker_basic():
    chunker = HierarchicalChunker(chunk_size=512, chunk_overlap=50)
    text = "This is a test document. " * 100
    
    chunks = chunker.chunk(text)
    
    assert len(chunks) > 0
    assert all("text" in chunk for chunk in chunks)
    assert all("metadata" in chunk for chunk in chunks)

def test_chunker_preserves_context():
    chunker = HierarchicalChunker(chunk_size=100, chunk_overlap=20)
    text = "First paragraph. " * 10 + "\n\n" + "Second paragraph. " * 10
    
    chunks = chunker.chunk(text)
    
    # Each chunk should have parent context
    assert all("parent_context" in chunk["metadata"] for chunk in chunks)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_ingestion/test_chunker.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement hierarchical chunker**

```python
# backend/app/ingestion/chunker.py
import re
from typing import Any

class HierarchicalChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(self, text: str, metadata: dict = None) -> list[dict[str, Any]]:
        """
        Split text into hierarchical chunks with parent context.
        
        Returns list of chunks, each with:
        - text: str
        - metadata: dict (includes parent_context)
        """
        # Split into paragraphs first
        paragraphs = re.split(r"\n\n+", text.strip())
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para.split())
            
            if current_size + para_size > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "parent_context": chunk_text,
                        "chunk_index": len(chunks),
                        **(metadata or {})
                    }
                })
                
                # Keep overlap
                overlap_words = []
                overlap_size = 0
                for word in reversed(current_chunk):
                    if overlap_size + len(word.split()) > self.chunk_overlap:
                        break
                    overlap_words.insert(0, word)
                    overlap_size += len(word.split())
                
                current_chunk = overlap_words
                current_size = overlap_size
            
            current_chunk.append(para)
            current_size += para_size
        
        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "parent_context": chunk_text,
                    "chunk_index": len(chunks),
                    **(metadata or {})
                }
            })
        
        return chunks
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_ingestion/test_chunker.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat: add hierarchical chunker with parent context"
```

---

### Task 6: LM Studio Embedder

**Files:**
- Create: `backend/app/ingestion/embedder.py`
- Test: `backend/tests/test_ingestion/test_embedder.py`

- [ ] **Step 1: Write failing test for embedder**

```python
# backend/tests/test_ingestion/test_embedder.py
import pytest
from app.ingestion.embedder import LMStudioEmbedder

@pytest.mark.asyncio
async def test_embedder_connection():
    embedder = LMStudioEmbedder(base_url="http://localhost:1234")
    is_connected = await embedder.check_connection()
    # This will fail if LM Studio is not running, which is expected
    assert isinstance(is_connected, bool)

@pytest.mark.asyncio
async def test_embedder_embed_text():
    embedder = LMStudioEmbedder(base_url="http://localhost:1234", model="nomic-embed-text-v1.5")
    texts = ["Hello world", "Test document"]
    
    embeddings = await embedder.embed(texts)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) > 0  # Should have embedding dimensions
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_ingestion/test_embedder.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement LM Studio embedder**

```python
# backend/app/ingestion/embedder.py
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class LMStudioEmbedder:
    def __init__(self, base_url: str = "http://localhost:1234", model: str = "nomic-embed-text-v1.5"):
        self.base_url = base_url
        self.model = model
    
    async def check_connection(self) -> bool:
        """Check if LM Studio is running and accessible."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/v1/models", timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a list of texts using LM Studio.
        
        Returns list of embedding vectors.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/embeddings",
                json={
                    "model": self.model,
                    "input": texts
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract embeddings from response
            embeddings = [item["embedding"] for item in data["data"]]
            return embeddings
```

- [ ] **Step 4: Run test to verify it passes (requires LM Studio running)**

```bash
cd backend
pytest tests/test_ingestion/test_embedder.py -v
```

Expected: Tests PASS if LM Studio is running, or skip if not available

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat: add LM Studio embedder with retry logic"
```

---

### Task 7: Document Indexer

**Files:**
- Create: `backend/app/ingestion/indexer.py`
- Test: `backend/tests/test_ingestion/test_indexer.py`

- [ ] **Step 1: Write failing test for indexer**

```python
# backend/tests/test_ingestion/test_indexer.py
import pytest
from pathlib import Path
from app.ingestion.indexer import DocumentIndexer
from app.ingestion.embedder import LMStudioEmbedder
from app.retrieval.qdrant_client import QdrantClient

@pytest.mark.asyncio
async def test_indexer_pipeline():
    embedder = LMStudioEmbedder()
    qdrant = QdrantClient()
    indexer = DocumentIndexer(embedder, qdrant)
    
    # Create a test markdown file
    test_file = Path("/tmp/test_doc.md")
    test_file.write_text("# Test\n\nThis is a test document.")
    
    result = await indexer.index_file(str(test_file), collection_id="test-collection")
    
    assert result["status"] == "success"
    assert result["chunks_indexed"] > 0
    
    # Cleanup
    test_file.unlink()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_ingestion/test_indexer.py -v
```

Expected: FAIL with "ModuleNotFoundError"
```

- [ ] **Step 3: Implement document indexer**

```python
# backend/app/ingestion/indexer.py
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Any

from app.ingestion.parsers.base import BaseParser
from app.ingestion.parsers.pdf import PDFParser
from app.ingestion.parsers.docx import DOCXParser
from app.ingestion.parsers.excel import ExcelParser
from app.ingestion.parsers.markdown import MarkdownParser
from app.ingestion.parsers.html import HTMLParser
from app.ingestion.chunker import HierarchicalChunker
from app.ingestion.embedder import LMStudioEmbedder
from app.retrieval.qdrant_client import QdrantClient

class DocumentIndexer:
    def __init__(self, embedder: LMStudioEmbedder, qdrant: QdrantClient):
        self.embedder = embedder
        self.qdrant = qdrant
        self.chunker = HierarchicalChunker(chunk_size=512, chunk_overlap=50)
        self.parsers = {
            ".pdf": PDFParser(),
            ".docx": DOCXParser(),
            ".xlsx": ExcelParser(),
            ".md": MarkdownParser(),
            ".html": HTMLParser(),
            ".htm": HTMLParser(),
        }
    
    def _get_parser(self, file_path: str) -> BaseParser:
        ext = Path(file_path).suffix.lower()
        parser = self.parsers.get(ext)
        if not parser:
            raise ValueError(f"Unsupported file type: {ext}")
        return parser
    
    def _generate_document_id(self, file_path: str) -> str:
        return hashlib.md5(file_path.encode()).hexdigest()
    
    async def index_file(self, file_path: str, collection_id: str) -> dict[str, Any]:
        """
        Index a single file: parse → chunk → embed → store.
        
        Returns dict with status and metadata.
        """
        try:
            parser = self._get_parser(file_path)
            with open(file_path, "rb") as f:
                content = f.read()
            parsed = parser.parse(content)
            
            chunks = self.chunker.chunk(parsed["text"], metadata={
                "file_path": file_path,
                "collection_id": collection_id,
                "document_id": self._generate_document_id(file_path)
            })
            
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = await self.embedder.embed(chunk_texts)
            
            points = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                points.append({
                    "id": f"{self._generate_document_id(file_path)}_{i}",
                    "vector": embedding,
                    "payload": {
                        "text": chunk["text"],
                        "file_path": file_path,
                        "collection_id": collection_id,
                        "document_id": self._generate_document_id(file_path),
                        "chunk_index": i,
                        "parent_context": chunk["metadata"].get("parent_context", ""),
                        "indexed_at": datetime.utcnow().isoformat()
                    }
                })
            
            await self.qdrant.upsert(points)
            
            return {
                "status": "success",
                "chunks_indexed": len(chunks),
                "document_id": self._generate_document_id(file_path)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def remove_document(self, file_path: str):
        """Remove all chunks for a document from the index."""
        document_id = self._generate_document_id(file_path)
        await self.qdrant.delete_by_filter({
            "must": [{"key": "document_id", "match": {"value": document_id}}]
        })
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_ingestion/test_indexer.py -v
```

Expected: Test PASS (requires LM Studio and Qdrant running)

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat: add document indexer with parse-chunk-embed-store pipeline"
```

---

## Phase 3: Vector Search & Retrieval

### Task 8: Qdrant Client

**Files:**
- Create: `backend/app/retrieval/qdrant_client.py`
- Test: `backend/tests/test_retrieval/test_qdrant_client.py`

- [ ] **Step 1: Write failing test for Qdrant client**

```python
# backend/tests/test_retrieval/test_qdrant_client.py
import pytest
from app.retrieval.qdrant_client import QdrantClient

@pytest.mark.asyncio
async def test_qdrant_client_init():
    client = QdrantClient()
    assert client is not None

@pytest.mark.asyncio
async def test_qdrant_client_upsert_and_search():
    client = QdrantClient(collection_name="test_collection")
    
    await client.ensure_collection(vector_size=384)
    
    points = [
        {
            "id": "test_1",
            "vector": [0.1] * 384,
            "payload": {"text": "Test document 1", "collection_id": "test"}
        },
        {
            "id": "test_2",
            "vector": [0.2] * 384,
            "payload": {"text": "Test document 2", "collection_id": "test"}
        }
    ]
    await client.upsert(points)
    
    results = await client.search([0.1] * 384, limit=2)
    assert len(results) > 0

@pytest.mark.asyncio
async def test_qdrant_client_delete():
    client = QdrantClient(collection_name="test_collection")
    await client.delete(["test_1", "test_2"])
    
    results = await client.search([0.1] * 384, limit=10)
    assert len(results) == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_retrieval/test_qdrant_client.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement Qdrant client**

```python
# backend/app/retrieval/qdrant_client.py
from qdrant_client import QdrantClient as QdrantClientLib
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.config import settings

class QdrantClient:
    def __init__(self, collection_name: str = "documents"):
        self.client = QdrantClientLib(path=str(settings.qdrant_path))
        self.collection_name = collection_name
    
    async def ensure_collection(self, vector_size: int = 384):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
    
    async def upsert(self, points: list[dict]):
        """Insert or update points in the collection."""
        point_structs = [
            PointStruct(
                id=p["id"],
                vector=p["vector"],
                payload=p["payload"]
            )
            for p in points
        ]
        self.client.upsert(
            collection_name=self.collection_name,
            points=point_structs
        )
    
    async def search(self, vector: list[float], limit: int = 10, filter_dict: dict = None) -> list[dict]:
        """Search for similar vectors."""
        query_filter = None
        if filter_dict:
            conditions = []
            for key, value in filter_dict.items():
                conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )
            query_filter = Filter(must=conditions)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
            query_filter=query_filter
        )
        
        return [
            {
                "id": r.id,
                "score": r.score,
                "payload": r.payload
            }
            for r in results
        ]
    
    async def delete(self, point_ids: list[str]):
        """Delete points by IDs."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=point_ids
        )
    
    async def delete_by_filter(self, filter_dict: dict):
        """Delete points by filter."""
        conditions = []
        for key, value in filter_dict.items():
            if isinstance(value, dict) and "match" in value:
                conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value["match"]["value"]))
                )
        
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(must=conditions)
        )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_retrieval/test_qdrant_client.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat: add Qdrant embedded client wrapper"
```

---

### Task 9: Hybrid Search

**Files:**
- Create: `backend/app/retrieval/hybrid_search.py`
- Test: `backend/tests/test_retrieval/test_hybrid_search.py`

- [ ] **Step 1: Write failing test for hybrid search**

```python
# backend/tests/test_retrieval/test_hybrid_search.py
import pytest
from app.retrieval.hybrid_search import HybridSearch
from app.retrieval.qdrant_client import QdrantClient
from app.ingestion.embedder import LMStudioEmbedder

@pytest.mark.asyncio
async def test_hybrid_search():
    qdrant = QdrantClient(collection_name="test_hybrid")
    embedder = LMStudioEmbedder()
    hybrid = HybridSearch(qdrant, embedder)
    
    await qdrant.ensure_collection(vector_size=384)
    
    query = "test query"
    results = await hybrid.search(query, limit=5)
    
    assert isinstance(results, list)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_retrieval/test_hybrid_search.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement hybrid search**

```python
# backend/app/retrieval/hybrid_search.py
from typing import Any
from app.retrieval.qdrant_client import QdrantClient
from app.ingestion.embedder import LMStudioEmbedder

class HybridSearch:
    def __init__(self, qdrant: QdrantClient, embedder: LMStudioEmbedder):
        self.qdrant = qdrant
        self.embedder = embedder
    
    async def search(self, query: str, limit: int = 10, collection_id: str = None) -> list[dict[str, Any]]:
        """Search for documents matching the query."""
        query_embedding = await self.embedder.embed([query])
        query_vector = query_embedding[0]
        
        filter_dict = None
        if collection_id:
            filter_dict = {"collection_id": collection_id}
        
        results = await self.qdrant.search(
            vector=query_vector,
            limit=limit,
            filter_dict=filter_dict
        )
        
        formatted = []
        for r in results:
            formatted.append({
                "text": r["payload"]["text"],
                "score": r["score"],
                "file_path": r["payload"]["file_path"],
                "collection_id": r["payload"]["collection_id"],
                "document_id": r["payload"]["document_id"],
                "chunk_index": r["payload"]["chunk_index"],
                "parent_context": r["payload"].get("parent_context", "")
            })
        
        return formatted
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_retrieval/test_hybrid_search.py -v
```

Expected: Test PASS

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat: add hybrid search with vector similarity and filtering"
```

---

## Phase 4: LLM Providers

### Task 10: Base Provider Interface

**Files:**
- Create: `backend/app/llm/providers/base.py`
- Test: `backend/tests/test_llm/test_providers.py`

- [ ] **Step 1: Write failing test for base provider**

```python
# backend/tests/test_llm/test_providers.py
import pytest
from app.llm.providers.base import BaseLLMProvider

def test_base_provider_interface():
    assert hasattr(BaseLLMProvider, "chat")
    assert hasattr(BaseLLMProvider, "chat_with_tools")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_llm/test_providers.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement base provider**

```python
# backend/app/llm/providers/base.py
from abc import ABC, abstractmethod
from typing import Any

class BaseLLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> str:
        pass
    
    @abstractmethod
    async def chat_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> dict[str, Any]:
        pass
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_llm/test_providers.py -v
```

Expected: Test PASS

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat: add base LLM provider interface"
```

---

### Task 11: Provider Implementations

**Files:**
- Create: `backend/app/llm/providers/anthropic.py`
- Create: `backend/app/llm/providers/openai.py`
- Create: `backend/app/llm/providers/google.py`
- Create: `backend/app/llm/providers/custom.py`

- [ ] **Step 1: Implement Anthropic provider**

```python
# backend/app/llm/providers/anthropic.py
from anthropic import AsyncAnthropic
from app.llm.providers.base import BaseLLMProvider

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
    
    async def chat(self, messages: list[dict], **kwargs) -> str:
        system_msg = None
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append(msg)
        
        response = await self.client.messages.create(
            model=self.model,
            system=system_msg or "",
            messages=chat_messages,
            max_tokens=kwargs.get("max_tokens", 4096),
            temperature=kwargs.get("temperature", 0.7)
        )
        
        return response.content[0].text
    
    async def chat_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> dict:
        system_msg = None
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append(msg)
        
        response = await self.client.messages.create(
            model=self.model,
            system=system_msg or "",
            messages=chat_messages,
            tools=tools,
            max_tokens=kwargs.get("max_tokens", 4096)
        )
        
        result = {"content": ""}
        
        for block in response.content:
            if block.type == "text":
                result["content"] += block.text
            elif block.type == "tool_use":
                if "tool_calls" not in result:
                    result["tool_calls"] = []
                result["tool_calls"].append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })
        
        return result
```

- [ ] **Step 2: Implement OpenAI provider**

```python
# backend/app/llm/providers/openai.py
from openai import AsyncOpenAI
from app.llm.providers.base import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def chat(self, messages: list[dict], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096)
        )
        
        return response.choices[0].message.content
    
    async def chat_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            temperature=kwargs.get("temperature", 0.7)
        )
        
        message = response.choices[0].message
        result = {"content": message.content or ""}
        
        if message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "input": tc.function.arguments
                }
                for tc in message.tool_calls
            ]
        
        return result
```

- [ ] **Step 3: Implement Google provider**

```python
# backend/app/llm/providers/google.py
import google.generativeai as genai
from app.llm.providers.base import BaseLLMProvider

class GoogleProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    async def chat(self, messages: list[dict], **kwargs) -> str:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        
        response = await self.model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=kwargs.get("temperature", 0.7),
                max_output_tokens=kwargs.get("max_tokens", 4096)
            )
        )
        
        return response.text
    
    async def chat_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> dict:
        response = await self.chat(messages, **kwargs)
        return {"content": response}
```

- [ ] **Step 4: Implement custom OpenAI-compatible provider**

```python
# backend/app/llm/providers/custom.py
from openai import AsyncOpenAI
from app.llm.providers.base import BaseLLMProvider

class CustomProvider(BaseLLMProvider):
    def __init__(self, base_url: str, api_key: str = None, model: str = "default"):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key or "not-needed")
        self.model = model
    
    async def chat(self, messages: list[dict], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096)
        )
        
        return response.choices[0].message.content
    
    async def chat_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            temperature=kwargs.get("temperature", 0.7)
        )
        
        message = response.choices[0].message
        result = {"content": message.content or ""}
        
        if message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "input": tc.function.arguments
                }
                for tc in message.tool_calls
            ]
        
        return result
```

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat: add LLM provider implementations (Anthropic, OpenAI, Google, Custom)"
```

---

### Task 12: Unified LLM Client

**Files:**
- Create: `backend/app/llm/client.py`

- [ ] **Step 1: Implement unified LLM client**

```python
# backend/app/llm/client.py
from typing import Any
from app.llm.providers.base import BaseLLMProvider
from app.llm.providers.anthropic import AnthropicProvider
from app.llm.providers.openai import OpenAIProvider
from app.llm.providers.google import GoogleProvider
from app.llm.providers.custom import CustomProvider

class LLMClient:
    def __init__(self, provider_config: dict):
        provider_type = provider_config["type"]
        api_key = provider_config.get("api_key")
        model = provider_config.get("model")
        
        if provider_type == "anthropic":
            self.provider = AnthropicProvider(api_key=api_key, model=model)
        elif provider_type == "openai":
            self.provider = OpenAIProvider(api_key=api_key, model=model)
        elif provider_type == "google":
            self.provider = GoogleProvider(api_key=api_key, model=model)
        elif provider_type == "custom":
            base_url = provider_config.get("base_url")
            self.provider = CustomProvider(base_url=base_url, api_key=api_key, model=model)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    async def chat(self, messages: list[dict], **kwargs) -> str:
        return await self.provider.chat(messages, **kwargs)
    
    async def chat_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> dict[str, Any]:
        return await self.provider.chat_with_tools(messages, tools, **kwargs)
```

- [ ] **Step 2: Commit**

```bash
git add backend/
git commit -m "feat: add unified LLM client with provider abstraction"
```

---

## Phase 5: Agentic RAG

### Task 13: Query Planner

**Files:**
- Create: `backend/app/agentic/planner.py`
- Test: `backend/tests/test_agentic/test_planner.py`

- [ ] **Step 1: Write failing test for planner**

```python
# backend/tests/test_agentic/test_planner.py
import pytest
from app.agentic.planner import QueryPlanner
from app.llm.client import LLMClient

@pytest.mark.asyncio
async def test_planner_simple_query():
    """Test that simple queries are not decomposed."""
    provider_config = {
        "type": "openai",
        "api_key": "test-key",
        "model": "gpt-4o"
    }
    llm = LLMClient(provider_config)
    planner = QueryPlanner(llm)
    
    result = await planner.plan("What is machine learning?")
    
    assert result["needs_decomposition"] is False
    assert len(result["sub_queries"]) == 1
    assert result["sub_queries"][0] == "What is machine learning?"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_agentic/test_planner.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement query planner**

```python
# backend/app/agentic/planner.py
import json
from typing import Any
from app.llm.client import LLMClient

class QueryPlanner:
    def __init__(self, llm: LLMClient):
        self.llm = llm
    
    async def plan(self, query: str) -> dict[str, Any]:
        """
        Analyze query and determine if it needs decomposition.
        
        Returns dict with:
        - needs_decomposition: bool
        - sub_queries: list[str]
        - reasoning: str
        """
        system_prompt = """You are a query analyzer. Determine if the user's question needs to be broken down into sub-queries.

Simple queries (single concept, direct lookup) do NOT need decomposition.
Complex queries (multiple concepts, comparisons, multi-step reasoning) DO need decomposition.

Respond with JSON:
{
    "needs_decomposition": true/false,
    "sub_queries": ["query1", "query2"] or ["original_query"],
    "reasoning": "brief explanation"
}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        response = await self.llm.chat(messages, temperature=0.3)
        
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            # Fallback: assume no decomposition needed
            result = {
                "needs_decomposition": False,
                "sub_queries": [query],
                "reasoning": "Failed to parse response, using original query"
            }
        
        return result
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_agentic/test_planner.py -v
```

Expected: Test PASS (requires LLM API key)

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat: add query planner for decomposition"
```

---

### Task 14: Retrieval Evaluator

**Files:**
- Create: `backend/app/agentic/evaluator.py`
- Test: `backend/tests/test_agentic/test_evaluator.py`

- [ ] **Step 1: Write failing test for evaluator**

```python
# backend/tests/test_agentic/test_evaluator.py
import pytest
from app.agentic.evaluator import RetrievalEvaluator
from app.llm.client import LLMClient

@pytest.mark.asyncio
async def test_evaluator_high_confidence():
    """Test that relevant chunks get high confidence."""
    provider_config = {
        "type": "openai",
        "api_key": "test-key",
        "model": "gpt-4o"
    }
    llm = LLMClient(provider_config)
    evaluator = RetrievalEvaluator(llm)
    
    query = "What is machine learning?"
    chunks = [
        {
            "text": "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
            "score": 0.95
        }
    ]
    
    result = await evaluator.evaluate(query, chunks)
    
    assert result["confidence"] == "high"
    assert result["score"] >= 0.8
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_agentic/test_evaluator.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement retrieval evaluator**

```python
# backend/app/agentic/evaluator.py
import json
from typing import Any
from app.llm.client import LLMClient

class RetrievalEvaluator:
    def __init__(self, llm: LLMClient):
        self.llm = llm
    
    async def evaluate(self, query: str, chunks: list[dict]) -> dict[str, Any]:
        """
        Evaluate retrieval quality and determine confidence level.
        
        Returns dict with:
        - confidence: "high" | "medium" | "low"
        - score: float (0-1)
        - reasoning: str
        """
        if not chunks:
            return {
                "confidence": "low",
                "score": 0.0,
                "reasoning": "No chunks retrieved"
            }
        
        # Prepare chunks for evaluation
        chunks_text = "\n\n".join([
            f"[Chunk {i+1}] (score: {c.get('score', 0):.2f})\n{c['text']}"
            for i, c in enumerate(chunks[:5])  # Evaluate top 5
        ])
        
        system_prompt = """You are a retrieval quality evaluator. Assess whether the retrieved chunks adequately answer the user's question.

Consider:
- Relevance: Do the chunks directly address the question?
- Completeness: Is there enough information to provide a good answer?
- Quality: Are the chunks clear and well-structured?

Respond with JSON:
{
    "confidence": "high" | "medium" | "low",
    "score": 0.0-1.0,
    "reasoning": "brief explanation"
}

High confidence (0.8-1.0): Chunks directly and fully answer the question
Medium confidence (0.5-0.79): Chunks partially answer or need some inference
Low confidence (0.0-0.49): Chunks are irrelevant or insufficient"""
        
        user_prompt = f"Question: {query}\n\nRetrieved chunks:\n{chunks_text}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.llm.chat(messages, temperature=0.2)
        
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            # Fallback: use average score
            avg_score = sum(c.get("score", 0) for c in chunks) / len(chunks)
            result = {
                "confidence": "medium" if avg_score > 0.7 else "low",
                "score": avg_score,
                "reasoning": "Failed to parse response, using average score"
            }
        
        return result
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_agentic/test_evaluator.py -v
```

Expected: Test PASS (requires LLM API key)

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat: add retrieval evaluator for confidence scoring"
```

---

### Task 15: Self-Critic

**Files:**
- Create: `backend/app/agentic/critic.py`
- Test: `backend/tests/test_agentic/test_critic.py`

- [ ] **Step 1: Write failing test for critic**

```python
# backend/tests/test_agentic/test_critic.py
import pytest
from app.agentic.critic import SelfCritic
from app.llm.client import LLMClient

@pytest.mark.asyncio
async def test_critic_valid_answer():
    """Test that supported answers pass validation."""
    provider_config = {
        "type": "openai",
        "api_key": "test-key",
        "model": "gpt-4o"
    }
    llm = LLMClient(provider_config)
    critic = SelfCritic(llm)
    
    query = "What is machine learning?"
    answer = "Machine learning is a subset of AI that enables systems to learn from data."
    chunks = [
        {
            "text": "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
            "score": 0.95
        }
    ]
    
    result = await critic.critique(query, answer, chunks)
    
    assert result["is_supported"] is True
    assert result["score"] >= 0.8
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_agentic/test_critic.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement self-critic**

```python
# backend/app/agentic/critic.py
import json
from typing import Any
from app.llm.client import LLMClient

class SelfCritic:
    def __init__(self, llm: LLMClient):
        self.llm = llm
    
    async def critique(self, query: str, answer: str, chunks: list[dict]) -> dict[str, Any]:
        """
        Validate that the answer is supported by the retrieved chunks.
        
        Returns dict with:
        - is_supported: bool
        - score: float (0-1)
        - reasoning: str
        - hallucinations: list[str] (unsupported claims)
        """
        chunks_text = "\n\n".join([
            f"[Source {i+1}]\n{c['text']}"
            for i, c in enumerate(chunks)
        ])
        
        system_prompt = """You are an answer quality validator. Check if the generated answer is supported by the source chunks.

Look for:
- Factual accuracy: Are all claims in the answer supported by the sources?
- Hallucinations: Does the answer contain information NOT in the sources?
- Completeness: Does the answer adequately address the question based on available information?

Respond with JSON:
{
    "is_supported": true/false,
    "score": 0.0-1.0,
    "reasoning": "brief explanation",
    "hallucinations": ["claim1", "claim2"] or []
}

High score (0.8-1.0): Answer is fully supported by sources
Medium score (0.5-0.79): Answer is mostly supported but may have minor issues
Low score (0.0-0.49): Answer contains hallucinations or is not supported"""
        
        user_prompt = f"""Question: {query}

Generated Answer: {answer}

Source Chunks:
{chunks_text}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.llm.chat(messages, temperature=0.2)
        
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            # Fallback: assume supported
            result = {
                "is_supported": True,
                "score": 0.7,
                "reasoning": "Failed to parse response, assuming supported",
                "hallucinations": []
            }
        
        return result
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_agentic/test_critic.py -v
```

Expected: Test PASS (requires LLM API key)

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat: add self-critic for answer validation"
```

---

### Task 16: Agentic Controller

**Files:**
- Create: `backend/app/agentic/controller.py`
- Test: `backend/tests/test_agentic/test_controller.py`

- [ ] **Step 1: Write failing test for controller**

```python
# backend/tests/test_agentic/test_controller.py
import pytest
from app.agentic.controller import AgenticController
from app.llm.client import LLMClient
from app.retrieval.hybrid_search import HybridSearch

@pytest.mark.asyncio
async def test_controller_basic_query():
    """Test basic query processing through agentic loop."""
    provider_config = {
        "type": "openai",
        "api_key": "test-key",
        "model": "gpt-4o"
    }
    llm = LLMClient(provider_config)
    
    # Mock search (would need real Qdrant in practice)
    class MockSearch:
        async def search(self, query, limit=10, collection_id=None):
            return [
                {
                    "text": "Machine learning is a subset of AI.",
                    "score": 0.9,
                    "file_path": "test.md",
                    "collection_id": "test",
                    "document_id": "doc1",
                    "chunk_index": 0,
                    "parent_context": "Machine learning is a subset of AI."
                }
            ]
    
    search = MockSearch()
    controller = AgenticController(llm, search)
    
    result = await controller.process("What is machine learning?")
    
    assert "answer" in result
    assert "citations" in result
    assert "iterations" in result
    assert result["iterations"] <= 5
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_agentic/test_controller.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement agentic controller**

```python
# backend/app/agentic/controller.py
from typing import Any
from app.llm.client import LLMClient
from app.retrieval.hybrid_search import HybridSearch
from app.agentic.planner import QueryPlanner
from app.agentic.evaluator import RetrievalEvaluator
from app.agentic.critic import SelfCritic

class AgenticController:
    def __init__(self, llm: LLMClient, search: HybridSearch, max_iterations: int = 5):
        self.llm = llm
        self.search = search
        self.max_iterations = max_iterations
        self.planner = QueryPlanner(llm)
        self.evaluator = RetrievalEvaluator(llm)
        self.critic = SelfCritic(llm)
    
    async def process(self, query: str, collection_id: str = None, conversation_history: list[dict] = None) -> dict[str, Any]:
        """
        Process a query through the agentic RAG loop.
        
        Returns dict with:
        - answer: str
        - citations: list[dict]
        - iterations: int
        - reasoning: str
        """
        iteration = 0
        all_citations = []
        reasoning_steps = []
        
        # Step 1: Plan query
        plan = await self.planner.plan(query)
        reasoning_steps.append(f"Planning: {plan['reasoning']}")
        
        sub_queries = plan["sub_queries"]
        
        # Step 2: Process each sub-query
        for sub_query in sub_queries:
            if iteration >= self.max_iterations:
                break
            
            # Retrieve chunks
            chunks = await self.search.search(sub_query, limit=10, collection_id=collection_id)
            
            if not chunks:
                reasoning_steps.append(f"No results for: {sub_query}")
                continue
            
            # Evaluate retrieval quality
            evaluation = await self.evaluator.evaluate(sub_query, chunks)
            reasoning_steps.append(f"Evaluation: {evaluation['reasoning']}")
            
            # If low confidence, could refine query (simplified: just continue)
            if evaluation["confidence"] == "low":
                reasoning_steps.append("Low confidence, but continuing with available chunks")
            
            # Generate answer for this sub-query
            answer = await self._generate_answer(sub_query, chunks, conversation_history)
            
            # Self-critique
            critique = await self.critic.critique(sub_query, answer, chunks)
            reasoning_steps.append(f"Critique: {critique['reasoning']}")
            
            # If answer is supported, add to results
            if critique["is_supported"]:
                all_citations.extend([
                    {
                        "text": chunk["text"],
                        "file_path": chunk["file_path"],
                        "document_id": chunk["document_id"],
                        "chunk_index": chunk["chunk_index"],
                        "score": chunk["score"],
                        "parent_context": chunk.get("parent_context", "")
                    }
                    for chunk in chunks[:3]  # Top 3 citations
                ])
            
            iteration += 1
        
        # Step 3: Generate final answer
        final_answer = await self._generate_final_answer(query, all_citations, conversation_history)
        
        return {
            "answer": final_answer,
            "citations": all_citations,
            "iterations": iteration,
            "reasoning": "\n".join(reasoning_steps)
        }
    
    async def _generate_answer(self, query: str, chunks: list[dict], history: list[dict] = None) -> str:
        """Generate answer for a sub-query."""
        context = "\n\n".join([c["text"] for c in chunks[:5]])
        
        system_prompt = """You are a helpful assistant. Answer the question based on the provided context.
Be concise and accurate. Cite sources using [1], [2], etc."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            messages.extend(history[-10:])  # Last 10 messages
        
        messages.append({
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {query}"
        })
        
        return await self.llm.chat(messages, temperature=0.7)
    
    async def _generate_final_answer(self, query: str, citations: list[dict], history: list[dict] = None) -> str:
        """Generate final comprehensive answer."""
        if not citations:
            return "I couldn't find relevant information to answer your question."
        
        context = "\n\n".join([c["text"] for c in citations[:5]])
        
        system_prompt = """You are a helpful assistant. Provide a comprehensive answer to the question based on the provided context.
Use citations [1], [2], etc. to reference sources. Be clear and well-structured."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            messages.extend(history[-10:])
        
        messages.append({
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {query}"
        })
        
        return await self.llm.chat(messages, temperature=0.7)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_agentic/test_controller.py -v
```

Expected: Test PASS (requires LLM API key)

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat: add agentic controller with iteration loop"
```

---

## Phase 6: Production Components

### Task 17: GPTCache Integration

**Files:**
- Create: `backend/app/cache/gpt_cache.py`

- [ ] **Step 1: Implement GPTCache wrapper**

```python
# backend/app/cache/gpt_cache.py
from gptcache import cache
from gptcache.adapter import openai as gptcache_openai
from gptcache.embedding import Onnx
from gptcache.manager import CacheBase, VectorBase, manager_factory
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation
from app.config import settings

class GPTCacheWrapper:
    def __init__(self):
        # Initialize cache with SQLite backend
        self.data_manager = manager_factory(
            sql_conflict_resolution="replace",
            sqlite_path=str(settings.cache_path),
        )
        
        # Initialize embedding model
        self.embedding = Onnx()
        
        # Initialize cache
        cache.init(
            embedding_func=self.embedding.to_embeddings,
            data_manager=self.data_manager,
            similarity_evaluation=SearchDistanceEvaluation(),
        )
    
    def get_cache(self):
        """Get the cache instance for use with LLM clients."""
        return cache
```

- [ ] **Step 2: Commit**

```bash
git add backend/
git commit -m "feat: add GPTCache semantic cache wrapper"
```

---

### Task 18: Arize Phoenix Tracing

**Files:**
- Create: `backend/app/tracing/phoenix.py`

- [ ] **Step 1: Implement Phoenix setup**

```python
# backend/app/tracing/phoenix.py
import phoenix as px
from app.config import settings

class PhoenixTracer:
    def __init__(self):
        self.session = None
    
    def start(self):
        """Start Phoenix tracing session."""
        if not settings.phoenix_enabled:
            return
        
        try:
            # Launch Phoenix in embedded mode
            px.launch_app()
            self.session = px.Client()
            print(f"Phoenix tracing started at http://localhost:{settings.phoenix_port}")
        except Exception as e:
            print(f"Failed to start Phoenix tracing: {e}")
    
    def stop(self):
        """Stop Phoenix tracing session."""
        if self.session:
            try:
                px.close_app()
            except Exception:
                pass
```

- [ ] **Step 2: Commit**

```bash
git add backend/
git commit -m "feat: add Arize Phoenix embedded tracing"
```

---

### Task 19: Ragas Evaluation

**Files:**
- Create: `backend/app/evaluation/ragas_eval.py`

- [ ] **Step 1: Implement Ragas evaluation runner**

```python
# backend/app/evaluation/ragas_eval.py
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset

class RagasEvaluator:
    def __init__(self):
        self.metrics = [faithfulness, answer_relevancy, context_precision, context_recall]
    
    def evaluate_batch(self, queries: list[str], answers: list[str], contexts: list[list[str]], ground_truths: list[str] = None) -> dict:
        """
        Evaluate a batch of RAG responses.
        
        Args:
            queries: List of user queries
            answers: List of generated answers
            contexts: List of context lists (retrieved chunks per query)
            ground_truths: Optional list of ground truth answers
        
        Returns:
            Dict with metric scores
        """
        data = {
            "question": queries,
            "answer": answers,
            "contexts": contexts,
        }
        
        if ground_truths:
            data["ground_truth"] = ground_truths
        
        dataset = Dataset.from_dict(data)
        
        results = evaluate(dataset, metrics=self.metrics)
        
        return {
            "faithfulness": results["faithfulness"],
            "answer_relevancy": results["answer_relevancy"],
            "context_precision": results["context_precision"],
            "context_recall": results.get("context_recall", None)
        }
```

- [ ] **Step 2: Commit**

```bash
git add backend/
git commit -m "feat: add Ragas evaluation runner"
```

---

## Phase 7: API Routes

### Task 20: Collection API Routes

**Files:**
- Create: `backend/app/api/routes/collections.py`

- [ ] **Step 1: Implement collection routes**

```python
# backend/app/api/routes/collections.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.database.repositories.collections import CollectionRepository
from pydantic import BaseModel

router = APIRouter(prefix="/collections", tags=["collections"])

class CollectionCreate(BaseModel):
    name: str
    description: str = None

class CollectionUpdate(BaseModel):
    name: str = None
    description: str = None

class CollectionResponse(BaseModel):
    id: str
    name: str
    description: str
    created_at: str
    updated_at: str

@router.get("/", response_model=list[CollectionResponse])
async def list_collections(session: AsyncSession = Depends(get_db_session)):
    repo = CollectionRepository(session)
    collections = await repo.get_all()
    return [
        CollectionResponse(
            id=c.id,
            name=c.name,
            description=c.description or "",
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat()
        )
        for c in collections
    ]

@router.post("/", response_model=CollectionResponse)
async def create_collection(data: CollectionCreate, session: AsyncSession = Depends(get_db_session)):
    repo = CollectionRepository(session)
    collection = await repo.create(name=data.name, description=data.description)
    return CollectionResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description or "",
        created_at=collection.created_at.isoformat(),
        updated_at=collection.updated_at.isoformat()
    )

@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(collection_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = CollectionRepository(session)
    collection = await repo.get_by_id(collection_id)
    if not collection:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Collection not found")
    return CollectionResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description or "",
        created_at=collection.created_at.isoformat(),
        updated_at=collection.updated_at.isoformat()
    )

@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(collection_id: str, data: CollectionUpdate, session: AsyncSession = Depends(get_db_session)):
    repo = CollectionRepository(session)
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    collection = await repo.update(collection_id, **update_data)
    return CollectionResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description or "",
        created_at=collection.created_at.isoformat(),
        updated_at=collection.updated_at.isoformat()
    )

@router.delete("/{collection_id}")
async def delete_collection(collection_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = CollectionRepository(session)
    await repo.delete(collection_id)
    return {"status": "deleted"}
```

- [ ] **Step 2: Commit**

```bash
git add backend/
git commit -m "feat: add collection API routes"
```

---

### Task 21: Document API Routes

**Files:**
- Create: `backend/app/api/routes/documents.py`

- [ ] **Step 1: Implement document routes**

```python
# backend/app/api/routes/documents.py
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.database.repositories.documents import DocumentRepository
from app.database.repositories.collections import CollectionRepository
from app.ingestion.indexer import DocumentIndexer
from app.ingestion.embedder import LMStudioEmbedder
from app.retrieval.qdrant_client import QdrantClient
from pydantic import BaseModel
import os

router = APIRouter(prefix="/documents", tags=["documents"])

class DocumentResponse(BaseModel):
    id: str
    collection_id: str
    file_path: str
    file_type: str
    file_size: int
    status: str
    error_message: str = None
    created_at: str
    updated_at: str
    indexed_at: str = None

@router.get("/collection/{collection_id}", response_model=list[DocumentResponse])
async def list_documents(collection_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = DocumentRepository(session)
    documents = await repo.get_by_collection(collection_id)
    return [
        DocumentResponse(
            id=d.id,
            collection_id=d.collection_id,
            file_path=d.file_path,
            file_type=d.file_type,
            file_size=d.file_size,
            status=d.status,
            error_message=d.error_message,
            created_at=d.created_at.isoformat(),
            updated_at=d.updated_at.isoformat(),
            indexed_at=d.indexed_at.isoformat() if d.indexed_at else None
        )
        for d in documents
    ]

@router.post("/upload")
async def upload_document(
    collection_id: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session)
):
    # Save file temporarily
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    # Create document record
    doc_repo = DocumentRepository(session)
    document = await doc_repo.create(
        collection_id=collection_id,
        file_path=tmp_path,
        file_type=os.path.splitext(file.filename)[1].lstrip('.'),
        file_size=len(content)
    )
    
    # Index document
    embedder = LMStudioEmbedder()
    qdrant = QdrantClient()
    indexer = DocumentIndexer(embedder, qdrant)
    
    result = await indexer.index_file(tmp_path, collection_id)
    
    # Update status
    if result["status"] == "success":
        await doc_repo.update_status(document.id, "indexed")
    else:
        await doc_repo.update_status(document.id, "error", result.get("error"))
    
    return {
        "document_id": document.id,
        "status": result["status"],
        "chunks_indexed": result.get("chunks_indexed", 0)
    }

@router.delete("/{document_id}")
async def delete_document(document_id: str, session: AsyncSession = Depends(get_db_session)):
    doc_repo = DocumentRepository(session)
    document = await doc_repo.get_by_id(document_id)
    
    if document:
        # Remove from Qdrant
        embedder = LMStudioEmbedder()
        qdrant = QdrantClient()
        indexer = DocumentIndexer(embedder, qdrant)
        await indexer.remove_document(document.file_path)
        
        # Remove from database
        await doc_repo.delete(document_id)
    
    return {"status": "deleted"}
```

- [ ] **Step 2: Commit**

```bash
git add backend/
git commit -m "feat: add document API routes"
```

---

### Task 22: Conversation and Chat API Routes

**Files:**
- Create: `backend/app/api/routes/conversations.py`
- Create: `backend/app/api/routes/chat.py`

- [ ] **Step 1: Implement conversation routes**

```python
# backend/app/api/routes/conversations.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.database.repositories.conversations import ConversationRepository
from app.database.repositories.messages import MessageRepository
from pydantic import BaseModel

router = APIRouter(prefix="/conversations", tags=["conversations"])

class ConversationCreate(BaseModel):
    title: str
    collection_id: str = None

class ConversationResponse(BaseModel):
    id: str
    title: str
    collection_id: str = None
    summary: str = None
    created_at: str
    updated_at: str

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    citations: list = []
    created_at: str

@router.get("/", response_model=list[ConversationResponse])
async def list_conversations(session: AsyncSession = Depends(get_db_session)):
    repo = ConversationRepository(session)
    conversations = await repo.get_all()
    return [
        ConversationResponse(
            id=c.id,
            title=c.title,
            collection_id=c.collection_id,
            summary=c.summary,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat()
        )
        for c in conversations
    ]

@router.post("/", response_model=ConversationResponse)
async def create_conversation(data: ConversationCreate, session: AsyncSession = Depends(get_db_session)):
    repo = ConversationRepository(session)
    conversation = await repo.create(title=data.title, collection_id=data.collection_id)
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        collection_id=conversation.collection_id,
        summary=conversation.summary,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat()
    )

@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(conversation_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = MessageRepository(session)
    messages = await repo.get_by_conversation(conversation_id)
    return [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            citations=m.citations or [],
            created_at=m.created_at.isoformat()
        )
        for m in messages
    ]

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = ConversationRepository(session)
    await repo.delete(conversation_id)
    return {"status": "deleted"}
```

- [ ] **Step 2: Implement chat route**

```python
# backend/app/api/routes/chat.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.database.repositories.conversations import ConversationRepository
from app.database.repositories.messages import MessageRepository
from app.database.repositories.provider_configs import ProviderConfigRepository
from app.llm.client import LLMClient
from app.retrieval.hybrid_search import HybridSearch
from app.retrieval.qdrant_client import QdrantClient
from app.ingestion.embedder import LMStudioEmbedder
from app.agentic.controller import AgenticController
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    provider_config_id: str

class ChatResponse(BaseModel):
    answer: str
    citations: list
    iterations: int
    reasoning: str

@router.post("/", response_model=ChatResponse)
async def chat(data: ChatRequest, session: AsyncSession = Depends(get_db_session)):
    # Get conversation
    conv_repo = ConversationRepository(session)
    conversation = await conv_repo.get_by_id(data.conversation_id)
    if not conversation:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get message history
    msg_repo = MessageRepository(session)
    history = await msg_repo.get_recent(data.conversation_id, count=10)
    history_dicts = [{"role": m.role, "content": m.content} for m in history]
    
    # Get provider config
    provider_repo = ProviderConfigRepository(session)
    provider_config = await provider_repo.get_by_id(data.provider_config_id)
    if not provider_config:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Provider config not found")
    
    # Initialize LLM client
    # Note: In production, retrieve API key from keychain
    llm_config = {
        "type": provider_config.type,
        "api_key": "placeholder",  # Would retrieve from keychain
        "model": provider_config.model,
        "base_url": provider_config.base_url
    }
    llm = LLMClient(llm_config)
    
    # Initialize search
    embedder = LMStudioEmbedder()
    qdrant = QdrantClient()
    search = HybridSearch(qdrant, embedder)
    
    # Process query through agentic controller
    controller = AgenticController(llm, search)
    result = await controller.process(
        query=data.message,
        collection_id=conversation.collection_id,
        conversation_history=history_dicts
    )
    
    # Save user message
    await msg_repo.create(
        conversation_id=data.conversation_id,
        role="user",
        content=data.message
    )
    
    # Save assistant message
    await msg_repo.create(
        conversation_id=data.conversation_id,
        role="assistant",
        content=result["answer"],
        citations=result["citations"]
    )
    
    return ChatResponse(
        answer=result["answer"],
        citations=result["citations"],
        iterations=result["iterations"],
        reasoning=result["reasoning"]
    )
```

- [ ] **Step 3: Commit**

```bash
git add backend/
git commit -m "feat: add conversation and chat API routes"
```

---

### Task 23: Settings API Routes

**Files:**
- Create: `backend/app/api/routes/settings.py`

- [ ] **Step 1: Implement settings routes**

```python
# backend/app/api/routes/settings.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.database.repositories.provider_configs import ProviderConfigRepository
from app.ingestion.embedder import LMStudioEmbedder
from pydantic import BaseModel

router = APIRouter(prefix="/settings", tags=["settings"])

class ProviderConfigCreate(BaseModel):
    name: str
    type: str
    provider_name: str
    model: str
    base_url: str = None
    api_key: str = None

class ProviderConfigResponse(BaseModel):
    id: str
    name: str
    type: str
    provider_name: str
    model: str
    base_url: str = None

class LMStudioStatus(BaseModel):
    connected: bool
    url: str
    model: str = None

@router.get("/providers", response_model=list[ProviderConfigResponse])
async def list_providers(session: AsyncSession = Depends(get_db_session)):
    repo = ProviderConfigRepository(session)
    configs = await repo.get_all()
    return [
        ProviderConfigResponse(
            id=c.id,
            name=c.name,
            type=c.type,
            provider_name=c.provider_name,
            model=c.model,
            base_url=c.base_url
        )
        for c in configs
    ]

@router.post("/providers", response_model=ProviderConfigResponse)
async def create_provider(data: ProviderConfigCreate, session: AsyncSession = Depends(get_db_session)):
    repo = ProviderConfigRepository(session)
    # Note: In production, store api_key in keychain, not database
    config = await repo.create(
        name=data.name,
        type=data.type,
        provider_name=data.provider_name,
        model=data.model,
        base_url=data.base_url,
        api_key_ref="placeholder"  # Would be keychain reference
    )
    return ProviderConfigResponse(
        id=config.id,
        name=config.name,
        type=config.type,
        provider_name=config.provider_name,
        model=config.model,
        base_url=config.base_url
    )

@router.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = ProviderConfigRepository(session)
    await repo.delete(provider_id)
    return {"status": "deleted"}

@router.get("/lm-studio/status", response_model=LMStudioStatus)
async def check_lm_studio_status():
    from app.config import settings
    embedder = LMStudioEmbedder(base_url=settings.lm_studio_url)
    connected = await embedder.check_connection()
    
    return LMStudioStatus(
        connected=connected,
        url=settings.lm_studio_url,
        model=settings.embedding_model if connected else None
    )
```

- [ ] **Step 2: Commit**

```bash
git add backend/
git commit -m "feat: add settings API routes"
```

---

### Task 24: Wire Up All Routes

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: Update main.py to include all routes**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database.session import init_db
from app.tracing.phoenix import PhoenixTracer
from app.api.routes import collections, documents, conversations, chat, settings

phoenix_tracer = PhoenixTracer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    phoenix_tracer.start()
    yield
    # Shutdown
    phoenix_tracer.stop()

app = FastAPI(title="Doc Assistant Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(collections.router)
app.include_router(documents.router)
app.include_router(conversations.router)
app.include_router(chat.router)
app.include_router(settings.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

- [ ] **Step 2: Test that all routes are accessible**

```bash
cd backend
uvicorn app.main:app --reload
```

Expected: Server starts without errors, all routes accessible at http://127.0.0.1:8000/docs

- [ ] **Step 3: Commit**

```bash
git add backend/
git commit -m "feat: wire up all API routes in main.py"
```

---

## Phase 8: File Watcher

### Task 25: Auto-Watch Implementation

**Files:**
- Create: `backend/app/ingestion/watcher.py`

- [ ] **Step 1: Implement file system watcher**

```python
# backend/app/ingestion/watcher.py
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.ingestion.indexer import DocumentIndexer
from app.ingestion.embedder import LMStudioEmbedder
from app.retrieval.qdrant_client import QdrantClient
from app.database.session import get_db_session, async_session
from app.database.repositories.documents import DocumentRepository
import asyncio

class DocumentEventHandler(FileSystemEventHandler):
    def __init__(self, collection_id: str):
        self.collection_id = collection_id
        self.embedder = LMStudioEmbedder()
        self.qdrant = QdrantClient()
        self.indexer = DocumentIndexer(self.embedder, self.qdrant)
        self.debounce_timer = {}
    
    def on_created(self, event):
        if event.is_directory:
            return
        self._schedule_index(event.src_path)
    
    def on_modified(self, event):
        if event.is_directory:
            return
        self._schedule_index(event.src_path)
    
    def on_deleted(self, event):
        if event.is_directory:
            return
        # Remove from index
        asyncio.run(self.indexer.remove_document(event.src_path))
    
    def _schedule_index(self, file_path: str):
        """Debounce indexing to avoid rapid re-indexing."""
        # Cancel existing timer if any
        if file_path in self.debounce_timer:
            self.debounce_timer[file_path].cancel()
        
        # Schedule new indexing after 2 seconds
        import threading
        timer = threading.Timer(2.0, self._index_file, args=[file_path])
        self.debounce_timer[file_path] = timer
        timer.start()
    
    def _index_file(self, file_path: str):
        """Index a file asynchronously."""
        asyncio.run(self._async_index(file_path))
    
    async def _async_index(self, file_path: str):
        """Async indexing wrapper."""
        async with async_session() as session:
            doc_repo = DocumentRepository(session)
            
            # Check if document exists
            existing = await doc_repo.get_by_path(file_path)
            
            if existing:
                # Remove old chunks
                await self.indexer.remove_document(file_path)
            
            # Index file
            result = await self.indexer.index_file(file_path, self.collection_id)
            
            if result["status"] == "success":
                if existing:
                    await doc_repo.update_status(existing.id, "indexed")
                else:
                    # Create new document record
                    file_size = Path(file_path).stat().st_size
                    file_type = Path(file_path).suffix.lstrip('.')
                    await doc_repo.create(
                        collection_id=self.collection_id,
                        file_path=file_path,
                        file_type=file_type,
                        file_size=file_size
                    )
                    await doc_repo.update_status(existing.id if existing else "new", "indexed")
            else:
                if existing:
                    await doc_repo.update_status(existing.id, "error", result.get("error"))

class CollectionWatcher:
    def __init__(self, collection_id: str, path: str):
        self.collection_id = collection_id
        self.path = path
        self.observer = Observer()
        self.handler = DocumentEventHandler(collection_id)
    
    def start(self):
        """Start watching the directory."""
        self.observer.schedule(self.handler, self.path, recursive=True)
        self.observer.start()
    
    def stop(self):
        """Stop watching the directory."""
        self.observer.stop()
        self.observer.join()
```

- [ ] **Step 2: Commit**

```bash
git add backend/
git commit -m "feat: add file system auto-watch with debouncing"
```

---

## Phase 9: Frontend

### Task 26: Frontend Scaffolding

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`

- [ ] **Step 1: Create frontend directory structure**

```bash
mkdir -p frontend/src/components/Chat
mkdir -p frontend/src/components/Documents
mkdir -p frontend/src/components/Settings
mkdir -p frontend/src/components/Layout
mkdir -p frontend/src/pages
mkdir -p frontend/src/hooks
mkdir -p frontend/src/services
mkdir -p frontend/src/types
```

- [ ] **Step 2: Create package.json**

```json
{
  "name": "doc-assistant-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.2",
    "@tauri-apps/api": "^2.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.11",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "typescript": "^5.5.3",
    "vite": "^5.4.8"
  }
}
```

- [ ] **Step 3: Create vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 1420,
    strictPort: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
```

- [ ] **Step 4: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 5: Create src/main.tsx**

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

- [ ] **Step 6: Create src/App.tsx**

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Chat from './pages/Chat'
import Documents from './pages/Documents'
import Settings from './pages/Settings'
import Sidebar from './components/Layout/Sidebar'

function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', height: '100vh' }}>
        <Sidebar />
        <div style={{ flex: 1, overflow: 'auto' }}>
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
```

- [ ] **Step 7: Install dependencies**

```bash
cd frontend
pnpm install
```

Expected: Dependencies installed successfully

- [ ] **Step 8: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold frontend with React, Vite, and TypeScript"
```

---

### Task 27: API Service Layer

**Files:**
- Create: `frontend/src/services/api.ts`
- Create: `frontend/src/types/index.ts`

- [ ] **Step 1: Create TypeScript types**

```typescript
// frontend/src/types/index.ts
export interface Collection {
  id: string
  name: string
  description: string
  created_at: string
  updated_at: string
}

export interface Document {
  id: string
  collection_id: string
  file_path: string
  file_type: string
  file_size: number
  status: 'pending' | 'indexed' | 'error'
  error_message?: string
  created_at: string
  updated_at: string
  indexed_at?: string
}

export interface Conversation {
  id: string
  title: string
  collection_id?: string
  summary?: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  citations: Citation[]
  created_at: string
}

export interface Citation {
  text: string
  file_path: string
  document_id: string
  chunk_index: number
  score: number
  parent_context: string
}

export interface ProviderConfig {
  id: string
  name: string
  type: 'builtin' | 'custom'
  provider_name: string
  model: string
  base_url?: string
}

export interface ChatResponse {
  answer: string
  citations: Citation[]
  iterations: number
  reasoning: string
}

export interface LMStudioStatus {
  connected: boolean
  url: string
  model?: string
}
```

- [ ] **Step 2: Create API service**

```typescript
// frontend/src/services/api.ts
import type {
  Collection,
  Document,
  Conversation,
  Message,
  ProviderConfig,
  ChatResponse,
  LMStudioStatus
} from '../types'

const API_BASE = 'http://127.0.0.1:8000'

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`)
  }
  
  return response.json()
}

// Collections
export const collectionsApi = {
  list: () => request<Collection[]>('/collections/'),
  create: (data: { name: string; description?: string }) =>
    request<Collection>('/collections/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  get: (id: string) => request<Collection>(`/collections/${id}`),
  update: (id: string, data: { name?: string; description?: string }) =>
    request<Collection>(`/collections/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id: string) =>
    request<{ status: string }>(`/collections/${id}`, {
      method: 'DELETE',
    }),
}

// Documents
export const documentsApi = {
  list: (collectionId: string) =>
    request<Document[]>(`/documents/collection/${collectionId}`),
  upload: async (collectionId: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('collection_id', collectionId)
    
    const response = await fetch(`${API_BASE}/documents/upload?collection_id=${collectionId}`, {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`)
    }
    
    return response.json()
  },
  delete: (id: string) =>
    request<{ status: string }>(`/documents/${id}`, {
      method: 'DELETE',
    }),
}

// Conversations
export const conversationsApi = {
  list: () => request<Conversation[]>('/conversations/'),
  create: (data: { title: string; collection_id?: string }) =>
    request<Conversation>('/conversations/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getMessages: (conversationId: string) =>
    request<Message[]>(`/conversations/${conversationId}/messages`),
  delete: (id: string) =>
    request<{ status: string }>(`/conversations/${id}`, {
      method: 'DELETE',
    }),
}

// Chat
export const chatApi = {
  send: (data: {
    conversation_id: string
    message: string
    provider_config_id: string
  }) =>
    request<ChatResponse>('/chat/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
}

// Settings
export const settingsApi = {
  listProviders: () => request<ProviderConfig[]>('/settings/providers'),
  createProvider: (data: {
    name: string
    type: string
    provider_name: string
    model: string
    base_url?: string
    api_key?: string
  }) =>
    request<ProviderConfig>('/settings/providers', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  deleteProvider: (id: string) =>
    request<{ status: string }>(`settings/providers/${id}`, {
      method: 'DELETE',
    }),
  checkLMStudio: () => request<LMStudioStatus>('/settings/lm-studio/status'),
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/
git commit -m "feat: add API service layer and TypeScript types"
```

---

### Task 28: Sidebar Component

**Files:**
- Create: `frontend/src/components/Layout/Sidebar.tsx`

- [ ] **Step 1: Create Sidebar component**

```tsx
// frontend/src/components/Layout/Sidebar.tsx
import { Link, useLocation } from 'react-router-dom'

export default function Sidebar() {
  const location = useLocation()
  
  const isActive = (path: string) => location.pathname === path
  
  return (
    <div style={{
      width: '200px',
      backgroundColor: '#f5f5f5',
      padding: '20px',
      borderRight: '1px solid #ddd'
    }}>
      <h2 style={{ marginBottom: '20px' }}>Doc Assistant</h2>
      <nav>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          <li style={{ marginBottom: '10px' }}>
            <Link
              to="/"
              style={{
                textDecoration: 'none',
                color: isActive('/') ? '#0066cc' : '#333',
                fontWeight: isActive('/') ? 'bold' : 'normal'
              }}
            >
              💬 Chat
            </Link>
          </li>
          <li style={{ marginBottom: '10px' }}>
            <Link
              to="/documents"
              style={{
                textDecoration: 'none',
                color: isActive('/documents') ? '#0066cc' : '#333',
                fontWeight: isActive('/documents') ? 'bold' : 'normal'
              }}
            >
              📄 Documents
            </Link>
          </li>
          <li style={{ marginBottom: '10px' }}>
            <Link
              to="/settings"
              style={{
                textDecoration: 'none',
                color: isActive('/settings') ? '#0066cc' : '#333',
                fontWeight: isActive('/settings') ? 'bold' : 'normal'
              }}
            >
              ⚙️ Settings
            </Link>
          </li>
        </ul>
      </nav>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/
git commit -m "feat: add sidebar navigation component"
```

---

### Task 29: Chat Page

**Files:**
- Create: `frontend/src/pages/Chat.tsx`
- Create: `frontend/src/components/Chat/ChatWindow.tsx`
- Create: `frontend/src/components/Chat/MessageList.tsx`
- Create: `frontend/src/components/Chat/MessageInput.tsx`
- Create: `frontend/src/components/Chat/CitationCard.tsx`

- [ ] **Step 1: Create Chat page**

```tsx
// frontend/src/pages/Chat.tsx
import { useState, useEffect } from 'react'
import ChatWindow from '../components/Chat/ChatWindow'
import { conversationsApi, settingsApi } from '../services/api'
import type { Conversation, ProviderConfig } from '../types'

export default function Chat() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null)
  const [providers, setProviders] = useState<ProviderConfig[]>([])
  const [selectedProvider, setSelectedProvider] = useState<string>('')
  
  useEffect(() => {
    loadConversations()
    loadProviders()
  }, [])
  
  async function loadConversations() {
    try {
      const convs = await conversationsApi.list()
      setConversations(convs)
      if (convs.length > 0 && !currentConversation) {
        setCurrentConversation(convs[0])
      }
    } catch (error) {
      console.error('Failed to load conversations:', error)
    }
  }
  
  async function loadProviders() {
    try {
      const provs = await settingsApi.listProviders()
      setProviders(provs)
      if (provs.length > 0) {
        setSelectedProvider(provs[0].id)
      }
    } catch (error) {
      console.error('Failed to load providers:', error)
    }
  }
  
  async function createConversation() {
    try {
      const conv = await conversationsApi.create({
        title: `Chat ${new Date().toLocaleString()}`
      })
      setConversations([...conversations, conv])
      setCurrentConversation(conv)
    } catch (error) {
      console.error('Failed to create conversation:', error)
    }
  }
  
  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '20px' }}>
        <h1>Chat</h1>
        <button onClick={createConversation} style={{ marginRight: '10px' }}>
          + New Chat
        </button>
        <select
          value={selectedProvider}
          onChange={(e) => setSelectedProvider(e.target.value)}
          style={{ padding: '5px' }}
        >
          {providers.map(p => (
            <option key={p.id} value={p.id}>
              {p.name} ({p.model})
            </option>
          ))}
        </select>
      </div>
      
      {currentConversation && selectedProvider ? (
        <ChatWindow
          conversationId={currentConversation.id}
          providerConfigId={selectedProvider}
        />
      ) : (
        <p>Select a conversation or create a new one to start chatting.</p>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Create ChatWindow component**

```tsx
// frontend/src/components/Chat/ChatWindow.tsx
import { useState, useEffect } from 'react'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import { conversationsApi, chatApi } from '../../services/api'
import type { Message, Citation } from '../../types'

interface ChatWindowProps {
  conversationId: string
  providerConfigId: string
}

export default function ChatWindow({ conversationId, providerConfigId }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  
  useEffect(() => {
    loadMessages()
  }, [conversationId])
  
  async function loadMessages() {
    try {
      const msgs = await conversationsApi.getMessages(conversationId)
      setMessages(msgs)
    } catch (error) {
      console.error('Failed to load messages:', error)
    }
  }
  
  async function handleSend(message: string) {
    setLoading(true)
    try {
      // Add user message optimistically
      const userMsg: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: message,
        citations: [],
        created_at: new Date().toISOString()
      }
      setMessages([...messages, userMsg])
      
      // Send to API
      const response = await chatApi.send({
        conversation_id: conversationId,
        message,
        provider_config_id: providerConfigId
      })
      
      // Add assistant response
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        citations: response.citations,
        created_at: new Date().toISOString()
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (error) {
      console.error('Failed to send message:', error)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 150px)' }}>
      <MessageList messages={messages} />
      <MessageInput onSend={handleSend} disabled={loading} />
    </div>
  )
}
```

- [ ] **Step 3: Create MessageList component**

```tsx
// frontend/src/components/Chat/MessageList.tsx
import { useRef, useEffect } from 'react'
import CitationCard from './CitationCard'
import type { Message } from '../../types'

interface MessageListProps {
  messages: Message[]
}

export default function MessageList({ messages }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  return (
    <div style={{
      flex: 1,
      overflowY: 'auto',
      padding: '20px',
      backgroundColor: '#fff'
    }}>
      {messages.map(msg => (
        <div
          key={msg.id}
          style={{
            marginBottom: '20px',
            padding: '15px',
            borderRadius: '8px',
            backgroundColor: msg.role === 'user' ? '#e3f2fd' : '#f5f5f5',
            maxWidth: '80%',
            marginLeft: msg.role === 'user' ? 'auto' : '0'
          }}
        >
          <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
            {msg.role === 'user' ? 'You' : 'Assistant'}
          </div>
          <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
          
          {msg.citations && msg.citations.length > 0 && (
            <div style={{ marginTop: '15px' }}>
              <div style={{ fontWeight: 'bold', marginBottom: '10px' }}>Sources:</div>
              {msg.citations.map((citation, idx) => (
                <CitationCard key={idx} citation={citation} index={idx + 1} />
              ))}
            </div>
          )}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
```

- [ ] **Step 4: Create MessageInput component**

```tsx
// frontend/src/components/Chat/MessageInput.tsx
import { useState } from 'react'

interface MessageInputProps {
  onSend: (message: string) => void
  disabled: boolean
}

export default function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [message, setMessage] = useState('')
  
  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSend(message)
      setMessage('')
    }
  }
  
  return (
    <form onSubmit={handleSubmit} style={{
      padding: '20px',
      borderTop: '1px solid #ddd',
      backgroundColor: '#fff'
    }}>
      <div style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask a question about your documents..."
          disabled={disabled}
          style={{
            flex: 1,
            padding: '10px',
            borderRadius: '4px',
            border: '1px solid #ddd',
            fontSize: '14px'
          }}
        />
        <button
          type="submit"
          disabled={disabled || !message.trim()}
          style={{
            padding: '10px 20px',
            borderRadius: '4px',
            border: 'none',
            backgroundColor: '#0066cc',
            color: 'white',
            cursor: disabled ? 'not-allowed' : 'pointer',
            opacity: disabled ? 0.6 : 1
          }}
        >
          {disabled ? 'Sending...' : 'Send'}
        </button>
      </div>
    </form>
  )
}
```

- [ ] **Step 5: Create CitationCard component**

```tsx
// frontend/src/components/Chat/CitationCard.tsx
import { useState } from 'react'
import type { Citation } from '../../types'

interface CitationCardProps {
  citation: Citation
  index: number
}

export default function CitationCard({ citation, index }: CitationCardProps) {
  const [expanded, setExpanded] = useState(false)
  
  return (
    <div style={{
      marginBottom: '10px',
      padding: '10px',
      backgroundColor: '#fff',
      border: '1px solid #ddd',
      borderRadius: '4px',
      cursor: 'pointer'
    }} onClick={() => setExpanded(!expanded)}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <strong>[{index}]</strong> {citation.file_path.split('/').pop()}
          <span style={{ marginLeft: '10px', color: '#666', fontSize: '12px' }}>
            Score: {citation.score.toFixed(2)}
          </span>
        </div>
        <span>{expanded ? '▼' : '▶'}</span>
      </div>
      
      {expanded && (
        <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #eee' }}>
          <div style={{ fontSize: '13px', color: '#666', marginBottom: '5px' }}>
            Chunk {citation.chunk_index}
          </div>
          <div style={{ fontSize: '14px', lineHeight: '1.5' }}>
            {citation.parent_context || citation.text}
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 6: Commit**

```bash
git add frontend/
git commit -m "feat: add chat page with message list, input, and citation cards"
```

---

### Task 30: Documents Page

**Files:**
- Create: `frontend/src/pages/Documents.tsx`
- Create: `frontend/src/components/Documents/CollectionList.tsx`
- Create: `frontend/src/components/Documents/DocumentList.tsx`

- [ ] **Step 1: Create Documents page**

```tsx
// frontend/src/pages/Documents.tsx
import { useState, useEffect } from 'react'
import CollectionList from '../components/Documents/CollectionList'
import DocumentList from '../components/Documents/DocumentList'
import { collectionsApi } from '../services/api'
import type { Collection } from '../types'

export default function Documents() {
  const [collections, setCollections] = useState<Collection[]>([])
  const [selectedCollection, setSelectedCollection] = useState<Collection | null>(null)
  
  useEffect(() => {
    loadCollections()
  }, [])
  
  async function loadCollections() {
    try {
      const colls = await collectionsApi.list()
      setCollections(colls)
    } catch (error) {
      console.error('Failed to load collections:', error)
    }
  }
  
  async function createCollection() {
    const name = prompt('Collection name:')
    if (!name) return
    
    try {
      const coll = await collectionsApi.create({ name })
      setCollections([...collections, coll])
      setSelectedCollection(coll)
    } catch (error) {
      console.error('Failed to create collection:', error)
    }
  }
  
  return (
    <div style={{ padding: '20px' }}>
      <h1>Documents</h1>
      <button onClick={createCollection} style={{ marginBottom: '20px' }}>
        + New Collection
      </button>
      
      <div style={{ display: 'flex', gap: '20px' }}>
        <div style={{ width: '300px' }}>
          <CollectionList
            collections={collections}
            selected={selectedCollection}
            onSelect={setSelectedCollection}
          />
        </div>
        <div style={{ flex: 1 }}>
          {selectedCollection ? (
            <DocumentList collectionId={selectedCollection.id} />
          ) : (
            <p>Select a collection to view documents.</p>
          )}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create CollectionList component**

```tsx
// frontend/src/components/Documents/CollectionList.tsx
import type { Collection } from '../../types'

interface CollectionListProps {
  collections: Collection[]
  selected: Collection | null
  onSelect: (collection: Collection) => void
}

export default function CollectionList({ collections, selected, onSelect }: CollectionListProps) {
  return (
    <div style={{
      border: '1px solid #ddd',
      borderRadius: '4px',
      overflow: 'hidden'
    }}>
      <h3 style={{ padding: '10px', backgroundColor: '#f5f5f5', margin: 0 }}>
        Collections
      </h3>
      {collections.map(coll => (
        <div
          key={coll.id}
          onClick={() => onSelect(coll)}
          style={{
            padding: '10px',
            cursor: 'pointer',
            backgroundColor: selected?.id === coll.id ? '#e3f2fd' : '#fff',
            borderBottom: '1px solid #eee'
          }}
        >
          <div style={{ fontWeight: 'bold' }}>{coll.name}</div>
          {coll.description && (
            <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
              {coll.description}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
```

- [ ] **Step 3: Create DocumentList component**

```tsx
// frontend/src/components/Documents/DocumentList.tsx
import { useState, useEffect } from 'react'
import { documentsApi } from '../../services/api'
import type { Document } from '../../types'

interface DocumentListProps {
  collectionId: string
}

export default function DocumentList({ collectionId }: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [uploading, setUploading] = useState(false)
  
  useEffect(() => {
    loadDocuments()
  }, [collectionId])
  
  async function loadDocuments() {
    try {
      const docs = await documentsApi.list(collectionId)
      setDocuments(docs)
    } catch (error) {
      console.error('Failed to load documents:', error)
    }
  }
  
  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    
    setUploading(true)
    try {
      await documentsApi.upload(collectionId, file)
      await loadDocuments()
    } catch (error) {
      console.error('Failed to upload document:', error)
      alert('Upload failed')
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }
  
  async function handleDelete(docId: string) {
    if (!confirm('Delete this document?')) return
    
    try {
      await documentsApi.delete(docId)
      await loadDocuments()
    } catch (error) {
      console.error('Failed to delete document:', error)
    }
  }
  
  const statusIcon = (status: string) => {
    switch (status) {
      case 'indexed': return '✓'
      case 'pending': return '⏳'
      case 'error': return '✗'
      default: return '?'
    }
  }
  
  return (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <label style={{
          padding: '10px 20px',
          backgroundColor: '#0066cc',
          color: 'white',
          borderRadius: '4px',
          cursor: uploading ? 'wait' : 'pointer'
        }}>
          {uploading ? 'Uploading...' : 'Upload Document'}
          <input
            type="file"
            onChange={handleUpload}
            disabled={uploading}
            style={{ display: 'none' }}
            accept=".pdf,.docx,.xlsx,.md,.html"
          />
        </label>
      </div>
      
      <div style={{
        border: '1px solid #ddd',
        borderRadius: '4px',
        overflow: 'hidden'
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f5f5f5' }}>
              <th style={{ padding: '10px', textAlign: 'left' }}>File</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Type</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Size</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Status</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map(doc => (
              <tr key={doc.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '10px' }}>
                  {doc.file_path.split('/').pop()}
                </td>
                <td style={{ padding: '10px' }}>{doc.file_type}</td>
                <td style={{ padding: '10px' }}>
                  {(doc.file_size / 1024).toFixed(1)} KB
                </td>
                <td style={{ padding: '10px' }}>
                  <span title={doc.error_message || ''}>
                    {statusIcon(doc.status)} {doc.status}
                  </span>
                </td>
                <td style={{ padding: '10px' }}>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    style={{
                      padding: '5px 10px',
                      backgroundColor: '#dc3545',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
            {documents.length === 0 && (
              <tr>
                <td colSpan={5} style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
                  No documents yet. Upload a file to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: add documents page with collection and document management"
```

---

### Task 31: Settings Page

**Files:**
- Create: `frontend/src/pages/Settings.tsx`
- Create: `frontend/src/components/Settings/ModelConfig.tsx`
- Create: `frontend/src/components/Settings/EmbeddingConfig.tsx`

- [ ] **Step 1: Create Settings page**

```tsx
// frontend/src/pages/Settings.tsx
import ModelConfig from '../components/Settings/ModelConfig'
import EmbeddingConfig from '../components/Settings/EmbeddingConfig'

export default function Settings() {
  return (
    <div style={{ padding: '20px', maxWidth: '800px' }}>
      <h1>Settings</h1>
      
      <section style={{ marginBottom: '40px' }}>
        <h2>LLM Provider</h2>
        <ModelConfig />
      </section>
      
      <section style={{ marginBottom: '40px' }}>
        <h2>Embeddings</h2>
        <EmbeddingConfig />
      </section>
    </div>
  )
}
```

- [ ] **Step 2: Create ModelConfig component**

```tsx
// frontend/src/components/Settings/ModelConfig.tsx
import { useState, useEffect } from 'react'
import { settingsApi } from '../../services/api'
import type { ProviderConfig } from '../../types'

export default function ModelConfig() {
  const [providers, setProviders] = useState<ProviderConfig[]>([])
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    type: 'builtin',
    provider_name: 'openai',
    model: 'gpt-4o',
    base_url: '',
    api_key: ''
  })
  
  useEffect(() => {
    loadProviders()
  }, [])
  
  async function loadProviders() {
    try {
      const provs = await settingsApi.listProviders()
      setProviders(provs)
    } catch (error) {
      console.error('Failed to load providers:', error)
    }
  }
  
  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    try {
      await settingsApi.createProvider(formData)
      await loadProviders()
      setShowForm(false)
      setFormData({
        name: '',
        type: 'builtin',
        provider_name: 'openai',
        model: 'gpt-4o',
        base_url: '',
        api_key: ''
      })
    } catch (error) {
      console.error('Failed to create provider:', error)
    }
  }
  
  async function handleDelete(id: string) {
    try {
      await settingsApi.deleteProvider(id)
      await loadProviders()
    } catch (error) {
      console.error('Failed to delete provider:', error)
    }
  }
  
  return (
    <div>
      <button onClick={() => setShowForm(!showForm)} style={{ marginBottom: '20px' }}>
        {showForm ? 'Cancel' : '+ Add Provider'}
      </button>
      
      {showForm && (
        <form onSubmit={handleCreate} style={{
          padding: '20px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          <div style={{ marginBottom: '10px' }}>
            <label>Name: </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              required
              style={{ padding: '5px', width: '200px' }}
            />
          </div>
          
          <div style={{ marginBottom: '10px' }}>
            <label>Type: </label>
            <select
              value={formData.type}
              onChange={(e) => setFormData({...formData, type: e.target.value})}
              style={{ padding: '5px' }}
            >
              <option value="builtin">Built-in</option>
              <option value="custom">Custom (OpenAI-compatible)</option>
            </select>
          </div>
          
          {formData.type === 'builtin' ? (
            <div style={{ marginBottom: '10px' }}>
              <label>Provider: </label>
              <select
                value={formData.provider_name}
                onChange={(e) => setFormData({...formData, provider_name: e.target.value})}
                style={{ padding: '5px' }}
              >
                <option value="anthropic">Anthropic (Claude)</option>
                <option value="openai">OpenAI (GPT)</option>
                <option value="google">Google (Gemini)</option>
              </select>
            </div>
          ) : (
            <>
              <div style={{ marginBottom: '10px' }}>
                <label>Base URL: </label>
                <input
                  type="text"
                  value={formData.base_url}
                  onChange={(e) => setFormData({...formData, base_url: e.target.value})}
                  placeholder="http://localhost:1234/v1"
                  required
                  style={{ padding: '5px', width: '300px' }}
                />
              </div>
            </>
          )}
          
          <div style={{ marginBottom: '10px' }}>
            <label>Model: </label>
            <input
              type="text"
              value={formData.model}
              onChange={(e) => setFormData({...formData, model: e.target.value})}
              required
              style={{ padding: '5px', width: '200px' }}
            />
          </div>
          
          <div style={{ marginBottom: '10px' }}>
            <label>API Key: </label>
            <input
              type="password"
              value={formData.api_key}
              onChange={(e) => setFormData({...formData, api_key: e.target.value})}
              style={{ padding: '5px', width: '300px' }}
            />
          </div>
          
          <button type="submit" style={{
            padding: '10px 20px',
            backgroundColor: '#0066cc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}>
            Save Provider
          </button>
        </form>
      )}
      
      <div>
        {providers.map(provider => (
          <div
            key={provider.id}
            style={{
              padding: '15px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              marginBottom: '10px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <div>
              <div style={{ fontWeight: 'bold' }}>{provider.name}</div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                {provider.provider_name} / {provider.model}
                {provider.base_url && ` / ${provider.base_url}`}
              </div>
            </div>
            <button
              onClick={() => handleDelete(provider.id)}
              style={{
                padding: '5px 10px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Create EmbeddingConfig component**

```tsx
// frontend/src/components/Settings/EmbeddingConfig.tsx
import { useState, useEffect } from 'react'
import { settingsApi } from '../../services/api'
import type { LMStudioStatus } from '../../types'

export default function EmbeddingConfig() {
  const [status, setStatus] = useState<LMStudioStatus | null>(null)
  const [checking, setChecking] = useState(false)
  
  useEffect(() => {
    checkStatus()
  }, [])
  
  async function checkStatus() {
    setChecking(true)
    try {
      const s = await settingsApi.checkLMStudio()
      setStatus(s)
    } catch (error) {
      console.error('Failed to check LM Studio:', error)
    } finally {
      setChecking(false)
    }
  }
  
  return (
    <div style={{
      padding: '20px',
      border: '1px solid #ddd',
      borderRadius: '4px'
    }}>
      <div style={{ marginBottom: '15px' }}>
        <strong>Status: </strong>
        {checking ? (
          <span>Checking...</span>
        ) : status?.connected ? (
          <span style={{ color: 'green' }}>✓ Connected</span>
        ) : (
          <span style={{ color: 'red' }}>✗ Not Connected</span>
        )}
      </div>
      
      {status && (
        <>
          <div style={{ marginBottom: '10px' }}>
            <strong>URL: </strong> {status.url}
          </div>
          {status.model && (
            <div style={{ marginBottom: '10px' }}>
              <strong>Model: </strong> {status.model}
            </div>
          )}
        </>
      )}
      
      {!status?.connected && (
        <div style={{
          marginTop: '20px',
          padding: '15px',
          backgroundColor: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '4px'
        }}>
          <h4 style={{ marginTop: 0 }}>Setup Instructions:</h4>
          <ol style={{ lineHeight: '1.8' }}>
            <li>Download LM Studio from <a href="https://lmstudio.ai" target="_blank">lmstudio.ai</a></li>
            <li>Download an embedding model (e.g., nomic-embed-text-v1.5)</li>
            <li>Start the LM Studio server (default port: 1234)</li>
          </ol>
          <button
            onClick={checkStatus}
            style={{
              padding: '10px 20px',
              backgroundColor: '#0066cc',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Check Connection
          </button>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: add settings page with model and embedding configuration"
```

---

## Phase 10: Tauri Integration

### Task 32: Tauri Setup

**Files:**
- Create: `src-tauri/Cargo.toml`
- Create: `src-tauri/tauri.conf.json`
- Create: `src-tauri/src/main.rs`
- Create: `src-tauri/src/lib.rs`
- Create: `src-tauri/src/commands/mod.rs`
- Create: `src-tauri/src/commands/backend.rs`

- [ ] **Step 1: Initialize Tauri project**

```bash
pnpm create tauri-app
```

Select:
- Project name: doc-assistant
- Choose language: Rust
- Choose package manager: pnpm
- Choose UI template: React
- Choose UI flavor: TypeScript

Then move the generated `src-tauri` folder to the project root.

- [ ] **Step 2: Update tauri.conf.json to point to frontend**

```json
{
  "build": {
    "beforeDevCommand": "cd frontend && pnpm dev",
    "beforeBuildCommand": "cd frontend && pnpm build",
    "devPath": "http://localhost:1420",
    "distDir": "../frontend/dist"
  },
  "package": {
    "productName": "Doc Assistant",
    "version": "0.1.0"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "shell": {
        "all": false,
        "open": true
      }
    },
    "bundle": {
      "active": true,
      "targets": "all",
      "identifier": "com.docassistant.app",
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/128x128@2x.png",
        "icons/icon.icns",
        "icons/icon.ico"
      ]
    },
    "security": {
      "csp": null
    },
    "windows": [
      {
        "fullscreen": false,
        "resizable": true,
        "title": "Doc Assistant",
        "width": 1200,
        "height": 800
      }
    ],
    "sidecar": [
      {
        "path": "../backend/dist/backend",
        "name": "backend"
      }
    ]
  }
}
```

- [ ] **Step 3: Create backend command to manage Python sidecar**

```rust
// src-tauri/src/commands/backend.rs
use tauri::api::process::{Command, CommandChild};
use std::sync::Mutex;

pub struct BackendState {
    pub child: Mutex<Option<CommandChild>>,
}

#[tauri::command]
pub async fn start_backend(state: tauri::State<'_, BackendState>) -> Result<(), String> {
    let mut child_lock = state.child.lock().unwrap();
    
    if child_lock.is_some() {
        return Ok(()); // Already running
    }
    
    let (mut rx, child) = Command::new_sidecar("backend")
        .expect("failed to create backend command")
        .spawn()
        .expect("failed to spawn backend");
    
    *child_lock = Some(child);
    
    // Spawn a task to log output
    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            match event {
                tauri::api::process::StdoutLine(line) => println!("[Backend] {}", line),
                tauri::api::process::StderrLine(line) => eprintln!("[Backend Error] {}", line),
                _ => {}
            }
        }
    });
    
    Ok(())
}

#[tauri::command]
pub async fn stop_backend(state: tauri::State<'_, BackendState>) -> Result<(), String> {
    let mut child_lock = state.child.lock().unwrap();
    
    if let Some(child) = child_lock.take() {
        child.kill().map_err(|e| e.to_string())?;
    }
    
    Ok(())
}
```

- [ ] **Step 4: Update main.rs to register commands**

```rust
// src-tauri/src/main.rs
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;

use commands::backend::{start_backend, stop_backend, BackendState};
use std::sync::Mutex;

fn main() {
    tauri::Builder::default()
        .manage(BackendState {
            child: Mutex::new(None),
        })
        .invoke_handler(tauri::generate_handler![start_backend, stop_backend])
        .setup(|app| {
            let window = app.get_window("main").unwrap();
            window.show().unwrap();
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

- [ ] **Step 5: Commit Tauri setup**

```bash
git add src-tauri/
git commit -m "feat: add Tauri desktop app setup with backend sidecar"
```

---

## Phase 11: Final Integration

### Task 33: Integration Testing

**Files:**
- Create: `tests/integration/test_full_pipeline.py`

- [ ] **Step 1: Create integration test for full pipeline**

```python
# tests/integration/test_full_pipeline.py
import pytest
import asyncio
from pathlib import Path

@pytest.mark.asyncio
async def test_full_document_pipeline():
    """Test complete flow: upload → index → search → chat."""
    # This test requires:
    # 1. LM Studio running with embedding model
    # 2. At least one LLM provider configured
    # 3. Test document available
    
    # Skip if prerequisites not met
    pytest.skip("Requires LM Studio and LLM provider setup")
    
    # Test flow would be:
    # 1. Create collection
    # 2. Upload test document
    # 3. Wait for indexing to complete
    # 4. Create conversation
    # 5. Send chat message
    # 6. Verify response has citations
    # 7. Clean up

@pytest.mark.asyncio
async def test_agentic_rag_loop():
    """Test agentic RAG with query decomposition."""
    pytest.skip("Requires full setup")
    
    # Test flow would be:
    # 1. Index multiple related documents
    # 2. Ask complex multi-hop question
    # 3. Verify planner decomposed the query
    # 4. Verify multiple retrieval iterations
    # 5. Verify final answer cites multiple sources
```

- [ ] **Step 2: Run integration tests (if setup available)**

```bash
cd backend
pytest tests/integration/ -v
```

Expected: Tests skip if prerequisites not met, or pass if full setup available

- [ ] **Step 3: Commit integration tests**

```bash
git add tests/
git commit -m "test: add integration tests for full pipeline"
```

---

### Task 34: Build and Package

**Files:**
- Create: `scripts/build_backend.sh`
- Create: `scripts/build_frontend.sh`
- Create: `scripts/package.sh`

- [ ] **Step 1: Create backend build script**

```bash
#!/bin/bash
# scripts/build_backend.sh

set -e

echo "Building backend..."
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build with PyInstaller
pip install pyinstaller
pyinstaller --onefile --name backend app/main.py

# Move binary to dist
mkdir -p dist
mv dist/backend ../backend/dist/

echo "Backend built successfully"
```

- [ ] **Step 2: Create frontend build script**

```bash
#!/bin/bash
# scripts/build_frontend.sh

set -e

echo "Building frontend..."
cd frontend

# Install dependencies
pnpm install

# Build
pnpm build

echo "Frontend built successfully"
```

- [ ] **Step 3: Create package script**

```bash
#!/bin/bash
# scripts/package.sh

set -e

echo "Packaging Doc Assistant..."

# Build backend
./scripts/build_backend.sh

# Build frontend
./scripts/build_frontend.sh

# Build Tauri app
cd src-tauri
cargo tauri build

echo "Package created in src-tauri/target/release/bundle/"
```

- [ ] **Step 4: Make scripts executable**

```bash
chmod +x scripts/*.sh
```

- [ ] **Step 5: Commit build scripts**

```bash
git add scripts/
git commit -m "build: add build and packaging scripts"
```

---

## Phase 12: Documentation

### Task 35: User Documentation

**Files:**
- Create: `docs/USER_GUIDE.md`
- Create: `docs/INSTALLATION.md`
- Create: `docs/TROUBLESHOOTING.md`

- [ ] **Step 1: Create user guide**

```markdown
# Doc Assistant User Guide

## Getting Started

### Prerequisites
1. Install LM Studio from https://lmstudio.ai
2. Download an embedding model (e.g., nomic-embed-text-v1.5)
3. Start LM Studio server (default port: 1234)
4. Configure at least one LLM provider in Settings

### First Steps
1. Launch Doc Assistant
2. Go to Settings → Embeddings and verify LM Studio is connected
3. Go to Settings → LLM Provider and add your provider (Anthropic, OpenAI, etc.)
4. Go to Documents → Create a new collection
5. Upload documents (PDF, DOCX, XLSX, MD, HTML)
6. Go to Chat → Create a new conversation
7. Ask questions about your documents!

## Features

### Document Management
- **Collections**: Organize documents into logical groups
- **Auto-indexing**: Documents are automatically indexed when uploaded
- **File watching**: Changes to indexed files are automatically detected
- **Supported formats**: PDF, DOCX, XLSX, Markdown, HTML

### Chat
- **Citations**: Every answer includes source citations
- **Source cards**: Click citations to see exact text from documents
- **Conversation history**: All chats are saved and searchable
- **Collection scoping**: Chat with specific document collections or all documents

### Agentic RAG
- **Query decomposition**: Complex questions are automatically broken down
- **Multi-hop reasoning**: Answers can draw from multiple documents
- **Self-correction**: System validates answers against sources
- **Confidence scoring**: Low-confidence retrievals trigger additional searches

## Tips

### For Better Answers
- Use specific questions rather than broad topics
- Reference specific documents or sections when possible
- Ask follow-up questions to clarify or expand on answers

### For Better Performance
- Keep collections focused on related topics
- Remove outdated documents regularly
- Use descriptive collection names for easy identification

## Keyboard Shortcuts
- `Ctrl/Cmd + N`: New conversation
- `Ctrl/Cmd + Enter`: Send message
- `Esc`: Cancel current operation
```

- [ ] **Step 2: Create installation guide**

```markdown
# Installation Guide

## System Requirements
- Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- 8GB RAM minimum (16GB recommended)
- 2GB disk space
- Internet connection for LLM API access

## Installation Steps

### 1. Install LM Studio
1. Download from https://lmstudio.ai
2. Install and launch LM Studio
3. Search for and download an embedding model:
   - Recommended: `nomic-embed-text-v1.5`
   - Alternative: `bge-base-en-v1.5`
4. Start the server (click "Start Server" button)
5. Verify server is running on port 1234

### 2. Install Doc Assistant
#### Windows
1. Download `Doc-Assistant-Setup.exe`
2. Run installer
3. Launch from Start Menu

#### macOS
1. Download `Doc-Assistant.dmg`
2. Open and drag to Applications
3. Launch from Applications

#### Linux
1. Download `doc-assistant.deb` (Debian/Ubuntu) or `doc-assistant.rpm` (Fedora)
2. Install: `sudo dpkg -i doc-assistant.deb` or `sudo rpm -i doc-assistant.rpm`
3. Launch from applications menu or run `doc-assistant`

### 3. Configure LLM Provider
1. Open Doc Assistant
2. Go to Settings → LLM Provider
3. Click "+ Add Provider"
4. Choose provider type:
   - **Built-in**: Anthropic, OpenAI, or Google
   - **Custom**: Any OpenAI-compatible API
5. Enter API key and model name
6. Click "Save Provider"

### 4. Verify Setup
1. Go to Settings → Embeddings
2. Verify LM Studio shows "✓ Connected"
3. Go to Documents → Create a test collection
4. Upload a test document
5. Verify document shows "✓ indexed" status
6. Go to Chat → Ask a question about the document
7. Verify you receive an answer with citations

## Troubleshooting

### LM Studio Not Connecting
- Ensure LM Studio server is running (not just the app)
- Check that port 1234 is not blocked by firewall
- Try accessing http://localhost:1234/v1/models in browser

### Documents Not Indexing
- Check file format is supported (PDF, DOCX, XLSX, MD, HTML)
- Verify file is not corrupted
- Check backend logs for errors

### Slow Performance
- Reduce number of documents in a collection
- Ensure LM Studio is using GPU acceleration
- Check internet connection for LLM API calls
```

- [ ] **Step 3: Create troubleshooting guide**

```markdown
# Troubleshooting

## Common Issues

### "LM Studio Not Connected"\n**Cause**: LM Studio server is not running or not accessible.\n\n**Solution**:\n1. Open LM Studio\n2. Click "Start Server" button\n3. Verify server shows "Running" status\n4. Check port is 1234 (default)\n5. Try http://localhost:1234/v1/models in browser\n\n---\n\n### "Document Upload Failed"\n**Cause**: File format not supported or file is corrupted.\n\n**Solution**:\n1. Verify file format: PDF, DOCX, XLSX, MD, HTML\n2. Check file is not password-protected\n3. Try re-downloading or re-saving the file\n4. Check file size (max 100MB recommended)\n\n---\n\n### "Document Stuck in 'pending' Status"\n**Cause**: Backend indexing process encountered an error.\n\n**Solution**:\n1. Check backend logs for error messages\n2. Verify LM Studio is running\n3. Try deleting and re-uploading the document\n4. Check disk space (indexing requires temporary storage)\n\n---\n\n### "No Citations in Answer"\n**Cause**: Answer may be generated without sufficient context, or citations were not properly formatted.\n\n**Solution**:\n1. Verify documents are indexed (status = "indexed")\n2. Try rephrasing the question more specifically\n3. Check if question is answerable from your documents\n4. Review backend logs for retrieval errors\n\n---\n\n### "Slow Response Times"\n**Cause**: Multiple factors can contribute to slow performance.\n\n**Solution**:\n1. **LM Studio**: Enable GPU acceleration in LM Studio settings\n2. **LLM API**: Check internet connection speed\n3. **Document count**: Reduce number of documents per collection\n4. **Chunk size**: Smaller chunks = faster retrieval but more API calls\n5. **Agentic loops**: Complex queries may require multiple iterations\n\n---\n\n### "API Key Not Working"\n**Cause**: Invalid API key or provider configuration.\n\n**Solution**:\n1. Verify API key is correct (no extra spaces)\n2. Check API key has not expired\n3. Verify provider name matches (anthropic, openai, google)\n4. For custom providers, verify base_url is correct\n5. Test API key directly with provider's API\n\n---\n\n### "Backend Crashes on Startup"\n**Cause**: Missing dependencies or configuration errors.\n\n**Solution**:\n1. Check Python version (requires 3.11+)\n2. Verify all dependencies installed: `pip install -r requirements.txt`\n3. Check data directory permissions\n4. Review backend logs for specific error messages\n5. Try deleting `~/.doc-assistant/` to reset (WARNING: deletes all data)\n\n---\n\n## Getting Help\n\nIf you encounter issues not covered here:\n\n1. **Check logs**: \n   - Backend: `~/.doc-assistant/logs/backend.log`\n   - Frontend: Browser developer console (F12)\n\n2. **Verify prerequisites**:\n   - LM Studio running with embedding model\n   - LLM provider configured with valid API key\n   - Documents properly indexed\n\n3. **Reset and retry**:\n   - Delete problematic document and re-upload\n   - Create new conversation\n   - Restart Doc Assistant\n\n4. **Report issues**:\n   - Include error messages and logs\n   - Describe steps to reproduce\n   - Note system information (OS, versions)\n```

- [ ] **Step 4: Commit documentation**

```bash
git add docs/
git commit -m "docs: add user guide, installation guide, and troubleshooting"
```

---

### Task 36: Developer Documentation

**Files:**
- Create: `docs/ARCHITECTURE.md`
- Create: `docs/API_REFERENCE.md`
- Create: `docs/DEVELOPMENT.md`

- [ ] **Step 1: Create architecture documentation**

```markdown
# Architecture

## Overview

Doc Assistant is a local-first desktop application that provides RAG (Retrieval-Augmented Generation) capabilities for document Q&A. The system uses an agentic RAG architecture with query decomposition, iterative retrieval, and self-correction.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Tauri Desktop App                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │           React Frontend (TypeScript)            │   │
│  │  - Chat UI with citations                        │   │
│  │  - Document management                           │   │
│  │  - Settings & configuration                      │   │
│  └──────────────────────────────────────────────────┘   │
│                         ↕ HTTP/JSON                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Python FastAPI Backend (Sidecar)         │   │
│  │  - REST API endpoints                            │   │
│  │  - Agentic RAG controller                        │   │
│  │  - Document ingestion pipeline                   │   │
│  │  - LLM provider abstraction                      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                         ↕
    ┌────────────────────┼────────────────────┐
    │                    │                    │
┌───▼────┐        ┌─────▼─────┐        ┌─────▼─────┐
│ Qdrant │        │ LM Studio │        │Cloud APIs │
│(Vector)│        │(Embedding)│        │(LLM Chat) │
└────────┘        └───────────┘        └───────────┘
```

## Components

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Routing**: React Router v6
- **State**: React hooks (useState, useEffect)
- **Styling**: Inline styles (minimal CSS)

**Key Pages**:\n- `Chat.tsx`: Main chat interface with conversation management\n- `Documents.tsx`: Document and collection management\n- `Settings.tsx`: Provider and embedding configuration\n\n**Key Components**:\n- `ChatWindow`: Message list and input\n- `CitationCard`: Expandable source citations\n- `CollectionList`: Document collection browser\n- `DocumentList`: Document upload and status\n\n### Backend (Python + FastAPI)
- **Framework**: FastAPI 0.115\n- **Database**: SQLite with SQLAlchemy ORM\n- **Vector DB**: Qdrant (embedded mode)\n- **Document Parsing**: Unstructured.io\n- **LLM Clients**: anthropic, openai, google-generativeai\n\n**Key Modules**:\n- `app/api/routes/`: REST API endpoints\n- `app/agentic/`: Agentic RAG logic (planner, evaluator, critic, controller)\n- `app/ingestion/`: Document parsing, chunking, embedding, indexing\n- `app/retrieval/`: Qdrant client and hybrid search\n- `app/llm/providers/`: LLM provider implementations\n- `app/database/`: SQLAlchemy models and repositories\n\n### Agentic RAG Pipeline

```\nUser Query\n    ↓\n┌─────────────┐\n│   Planner   │ → Decompose into sub-queries\n└─────────────┘\n    ↓\n┌─────────────┐\n│  Retrieval  │ → Hybrid search (BM25 + vector)\n└─────────────┘\n    ↓\n┌─────────────┐\n│  Evaluator  │ → Score confidence (high/medium/low)\n└─────────────┘\n    ↓\n┌─────────────┐\n│  Generator  │ → Generate answer with citations\n└─────────────┘\n    ↓\n┌─────────────┐\n│   Critic    │ → Validate answer against sources\n└─────────────┘\n    ↓\n┌─────────────┐\n│ Controller  │ → Iterate if needed (max 5 loops)\n└─────────────┘\n    ↓\nFinal Answer with Citations\n```\n\n### Data Flow\n\n1. **Document Ingestion**:\n   ```\n   Upload → Parse → Chunk → Embed → Store in Qdrant\n   ```\n\n2. **Query Processing**:\n   ```\n   Query → Plan → Retrieve → Evaluate → Generate → Critique → Answer\n   ```\n\n3. **Conversation Management**:\n   ```\n   Message → Save to DB → Process → Save Response → Return\n   ```\n\n## Database Schema\n\n### SQLite Tables\n\n**collections**\n- id (UUID)\n- name (TEXT)\n- description (TEXT)\n- created_at (DATETIME)\n- updated_at (DATETIME)\n\n**documents**\n- id (UUID)\n- collection_id (UUID, FK)\n- file_path (TEXT)\n- file_type (TEXT)\n- file_size (INTEGER)\n- status (TEXT: pending|indexed|error)\n- error_message (TEXT)\n- created_at (DATETIME)\n- updated_at (DATETIME)\n- indexed_at (DATETIME)\n\n**conversations**\n- id (UUID)\n- title (TEXT)\n- collection_id (UUID, FK, nullable)\n- summary (TEXT)\n- created_at (DATETIME)\n- updated_at (DATETIME)\n\n**messages**\n- id (UUID)\n- conversation_id (UUID, FK)\n- role (TEXT: user|assistant|system)\n- content (TEXT)\n- citations (JSON)\n- created_at (DATETIME)\n\n**provider_configs**\n- id (UUID)\n- name (TEXT)\n- type (TEXT: builtin|custom)\n- provider_name (TEXT)\n- model (TEXT)\n- base_url (TEXT, nullable)\n- api_key_ref (TEXT)\n- created_at (DATETIME)\n\n### Qdrant Collections\n\n**documents** (vector collection)\n- Vector size: 384 (nomic-embed-text-v1.5)\n- Distance: Cosine\n- Payload fields:\n  - text (string)\n  - file_path (string)\n  - collection_id (string)\n  - document_id (string)\n  - chunk_index (integer)\n  - parent_context (string)\n  - indexed_at (string)\n\n## API Endpoints\n\n### Collections\n- `GET /collections/` - List all collections\n- `POST /collections/` - Create collection\n- `GET /collections/{id}` - Get collection\n- `PUT /collections/{id}` - Update collection\n- `DELETE /collections/{id}` - Delete collection\n\n### Documents\n- `GET /documents/collection/{id}` - List documents in collection\n- `POST /documents/upload` - Upload and index document\n- `DELETE /documents/{id}` - Delete document\n\n### Conversations\n- `GET /conversations/` - List conversations\n- `POST /conversations/` - Create conversation\n- `GET /conversations/{id}/messages` - Get messages\n- `DELETE /conversations/{id}` - Delete conversation\n\n### Chat\n- `POST /chat/` - Send message and get response\n\n### Settings\n- `GET /settings/providers` - List provider configs\n- `POST /settings/providers` - Create provider config\n- `DELETE /settings/providers/{id}` - Delete provider config\n- `GET /settings/lm-studio/status` - Check LM Studio connection\n\n## Technology Stack\n\n### Backend\n- Python 3.11+\n- FastAPI 0.115\n- SQLAlchemy 2.0 (async)\n- Qdrant-client 1.12\n- Unstructured 0.15\n- LangGraph 0.2\n- Anthropic, OpenAI, Google Generative AI clients\n- GPTCache 0.1\n- Arize Phoenix 5.6\n- Ragas 0.2\n- Tenacity 9.0\n- Watchdog 5.0\n\n### Frontend\n- React 18\n- TypeScript 5.5\n- Vite 5.4\n- React Router 6\n\n### Desktop\n- Tauri 2.x\n- Rust (sidecar management)\n\n## Security Considerations\n\n1. **API Keys**: Stored in system keychain (not database)\n2. **Local Processing**: All document processing happens locally\n3. **Network**: Only LLM API calls go over network\n4. **Data Privacy**: Documents never leave the machine (except chunks sent to LLM)\n\n## Performance Characteristics\n\n- **Document Indexing**: ~2-5 seconds per page (depends on LM Studio)\n- **Simple Query**: 1-2 seconds\n- **Complex Query (Agentic)**: 4-8 seconds (depends on iterations)\n- **Memory Usage**: ~500MB-1GB (depends on document count)\n- **Disk Usage**: ~100MB per 1000 document chunks\n\n## Scalability\n\n- **Documents**: Tested up to 10,000 documents\n- **Conversations**: No practical limit (SQLite handles millions)\n- **Concurrent Users**: Single-user desktop app (not designed for multi-user)\n```

- [ ] **Step 2: Create API reference**

```markdown
# API Reference

## Base URL

```\nhttp://127.0.0.1:8000\n```\n\n## Authentication\n+
No authentication required (local application).

## Endpoints

### Collections

#### List Collections
```http\nGET /collections/\n```\n\n**Response**:\n```json\n[\n  {\n    "id": "uuid",\n    "name": "string",\n    "description": "string",\n    "created_at": "ISO8601",\n    "updated_at": "ISO8601"\n  }\n]\n```\n\n#### Create Collection
```http\nPOST /collections/\nContent-Type: application/json\n\n{\n  "name": "string",\n  "description": "string" (optional)\n}\n```\n\n**Response**: Collection object\n\n#### Get Collection
```http\nGET /collections/{collection_id}\n```\n\n**Response**: Collection object\n\n#### Update Collection
```http\nPUT /collections/{collection_id}\nContent-Type: application/json\n\n{\n  "name": "string" (optional),\n  "description": "string" (optional)\n}\n```\n\n**Response**: Collection object\n\n#### Delete Collection
```http\nDELETE /collections/{collection_id}\n```\n\n**Response**:\n```json\n{\n  "status": "deleted"\n}\n```\n\n---\n\n### Documents\n\n#### List Documents\n+```http\nGET /documents/collection/{collection_id}\n```\n\n**Response**:\n```json\n[\n  {\n    "id": "uuid",\n    "collection_id": "uuid",\n    "file_path": "string",\n    "file_type": "string",\n    "file_size": 12345,\n    "status": "pending|indexed|error",\n    "error_message": "string" (optional),\n    "created_at": "ISO8601",\n    "updated_at": "ISO8601",\n    "indexed_at": "ISO8601" (optional)\n  }\n]\n```\n\n#### Upload Document
```http\nPOST /documents/upload?collection_id={collection_id}\nContent-Type: multipart/form-data\n\nfile: <binary file data>\n```\n\n**Supported formats**: PDF, DOCX, XLSX, MD, HTML\n\n**Response**:\n```json\n{\n  "document_id": "uuid",\n  "status": "success|error",\n  "chunks_indexed": 42\n}\n```\n\n#### Delete Document
```http\nDELETE /documents/{document_id}\n```\n\n**Response**:\n```json\n{\n  "status": "deleted"\n}\n```\n\n---\n\n### Conversations\n\n#### List Conversations
```http
GET /conversations/
```

**Response**:
```json
[
  {
    "id": "uuid",
    "title": "string",
    "collection_id": "uuid" (optional),
    "summary": "string" (optional),
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  }
]
```

#### Create Conversation
```http
POST /conversations/
Content-Type: application/json

{
  "title": "string",
  "collection_id": "uuid" (optional)
}
```

**Response**: Conversation object

#### Get Messages
```http
GET /conversations/{conversation_id}/messages
```

**Response**:
```json
[
  {
    "id": "uuid",
    "role": "user|assistant|system",
    "content": "string",
    "citations": [
      {
        "text": "string",
        "file_path": "string",
        "document_id": "string",
        "chunk_index": 0,
        "score": 0.95,
        "parent_context": "string"
      }
    ],
    "created_at": "ISO8601"
  }
]
```

#### Delete Conversation
```http
DELETE /conversations/{conversation_id}
```

**Response**:
```json
{
  "status": "deleted"
}
```

---

### Chat

#### Send Message
```http
POST /chat/
Content-Type: application/json

{
  "conversation_id": "uuid",
  "message": "string",
  "provider_config_id": "uuid"
}
```

**Response**:
```json
{
  "answer": "string",
  "citations": [
    {
      "text": "string",
      "file_path": "string",
      "document_id": "string",
      "chunk_index": 0,
      "score": 0.95,
      "parent_context": "string"
    }
  ],
  "iterations": 2,
  "reasoning": "string"
}
```

---

### Settings

#### List Providers
```http
GET /settings/providers
```

**Response**:
```json
[
  {
    "id": "uuid",
    "name": "string",
    "type": "builtin|custom",
    "provider_name": "string",
    "model": "string",
    "base_url": "string" (optional)
  }
]
```

#### Create Provider
```http
POST /settings/providers
Content-Type: application/json

{
  "name": "string",
  "type": "builtin|custom",
  "provider_name": "string",
  "model": "string",
  "base_url": "string" (optional, for custom),
  "api_key": "string" (optional)
}
```

**Response**: ProviderConfig object (without api_key)

#### Delete Provider
```http
DELETE /settings/providers/{provider_id}
```

**Response**:
```json
{
  "status": "deleted"
}
```

#### Check LM Studio Status
```http
GET /settings/lm-studio/status
```

**Response**:
```json
{
  "connected": true,
  "url": "http://localhost:1234",
  "model": "nomic-embed-text-v1.5"
}
```

---

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message"
}
```

Common status codes:
- `400` - Bad request (invalid input)
- `404` - Not found (resource doesn't exist)
- `500` - Internal server error
- `503` - Service unavailable (LM Studio not connected, LLM API error)
```

- [ ] **Step 3: Create development guide**

```markdown
# Development Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- pnpm
- Rust (for Tauri)
- LM Studio

## Setup

### 1. Clone repository
```bash
git clone <repo-url>
cd doc_assistant
```

### 2. Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend setup
```bash
cd frontend
pnpm install
```

### 4. LM Studio setup
1. Install LM Studio
2. Download `nomic-embed-text-v1.5` model
3. Start server on port 1234

## Running in Development

### Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Backend runs at http://127.0.0.1:8000
API docs at http://127.0.0.1:8000/docs

### Frontend
```bash
cd frontend
pnpm dev
```

Frontend runs at http://localhost:1420

### Tauri (desktop)
```bash
cd src-tauri
cargo tauri dev
```

## Running Tests

### Backend tests
```bash
cd backend
pytest tests/ -v
```

### With coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Specific test modules
```bash
pytest tests/test_ingestion/ -v
pytest tests/test_agentic/ -v
pytest tests/test_api/ -v
```

## Code Structure

### Backend modules
- `app/api/` - FastAPI routes
- `app/agentic/` - Agentic RAG logic
- `app/ingestion/` - Document processing
- `app/retrieval/` - Vector search
- `app/llm/` - LLM providers
- `app/database/` - Database models and repos
- `app/cache/` - GPTCache integration
- `app/tracing/` - Phoenix tracing
- `app/evaluation/` - Ragas evaluation

### Frontend structure
- `src/components/` - React components
- `src/pages/` - Page components
- `src/services/` - API client
- `src/types/` - TypeScript types
- `src/hooks/` - Custom hooks

## Adding a New LLM Provider

1. Create `backend/app/llm/providers/new_provider.py`
2. Implement `BaseLLMProvider` interface:
   ```python
   class NewProvider(BaseLLMProvider):
       async def chat(self, messages, **kwargs) -> str: ...
       async def chat_with_tools(self, messages, tools, **kwargs) -> dict: ...
   ```
3. Register in `backend/app/llm/client.py`:
   ```python
   elif provider_type == "new_provider":
       self.provider = NewProvider(api_key=api_key, model=model)
   ```
4. Update frontend `ModelConfig.tsx` to include new provider option

## Adding a New Document Parser

1. Create `backend/app/ingestion/parsers/new_format.py`
2. Implement `BaseParser` interface:
   ```python
   class NewFormatParser(BaseParser):
       def parse(self, content: str | bytes) -> dict:
           return {
               "text": "...",
               "metadata": {...},
               "elements": [...]
           }
   ```
3. Register in `backend/app/ingestion/indexer.py`:
   ```python
   self.parsers = {
       ...
       ".new": NewFormatParser(),
   }
   ```

## Debugging

### Backend logs
```bash
tail -f ~/.doc-assistant/logs/backend.log
```

### Phoenix traces
Open http://localhost:6006 in browser

### Qdrant inspection
```python
from qdrant_client import QdrantClient
client = QdrantClient(path="~/.doc-assistant/qdrant")
client.get_collections()
```

## Common Development Tasks

### Reset database
```bash
rm ~/.doc-assistant/app.db
```

### Reset vector index
```bash
rm -rf ~/.doc-assistant/qdrant
```

### Reset cache
```bash
rm ~/.doc-assistant/cache.db
```

### Full reset
```bash
rm -rf ~/.doc-assistant
```

## Performance Profiling

### Backend
```bash
python -m cProfile -o profile.out -m uvicorn app.main:app
snakeviz profile.out
```

### Frontend
Use React DevTools Profiler

## Building for Production

See `scripts/package.sh` for full build process.

### Backend only
```bash
./scripts/build_backend.sh
```

### Frontend only
```bash
./scripts/build_frontend.sh
```

### Full package
```bash
./scripts/package.sh
```

Output: `src-tauri/target/release/bundle/`

## Contributing

1. Fork repository
2. Create feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## Code Style

- **Backend**: Black formatter, 100 char line length
- **Frontend**: Prettier, ESLint
- **Types**: Strict TypeScript
- **Tests**: pytest with descriptive names

## License

MIT
```

- [ ] **Step 4: Commit developer documentation**

```bash
git add docs/
git commit -m "docs: add architecture, API reference, and development guide"
```

---

## Phase 13: Final Verification

### Task 37: End-to-End Verification

- [ ] **Step 1: Verify backend starts**

```bash
cd backend
uvicorn app.main:app --reload
```

Expected: Server starts, http://127.0.0.1:8000/health returns `{"status": "ok"}`

- [ ] **Step 2: Verify frontend starts**

```bash
cd frontend
pnpm dev
```

Expected: Frontend loads at http://localhost:1420

- [ ] **Step 3: Verify LM Studio connection**

```bash
curl http://localhost:1234/v1/models
```

Expected: Returns list of available models

- [ ] **Step 4: Run all backend tests**

```bash
cd backend
pytest tests/ -v --tb=short
```

Expected: All tests pass (except those requiring external services)

- [ ] **Step 5: Manual end-to-end test**

1. Start backend: `uvicorn app.main:app`
2. Start frontend: `pnpm dev`
3. Start LM Studio server
4. Open http://localhost:1420
5. Go to Settings → Add LLM provider with API key
6. Verify LM Studio shows "Connected"
7. Go to Documents → Create collection
8. Upload a test PDF
9. Wait for "indexed" status
10. Go to Chat → Create conversation
11. Ask question about the document
12. Verify answer appears with citations
13. Click citation card → verify it expands with source text

- [ ] **Step 6: Commit any fixes**

```bash
git add -A
git commit -m "fix: resolve issues found during end-to-end verification"
```

---

## Summary

This implementation plan covers the complete build of a local RAG assistant with:

**Backend (Python FastAPI)**:
- Database models and repositories (SQLite)
- Document ingestion pipeline (Unstructured.io)
- Hierarchical chunking
- LM Studio embedding integration
- Qdrant vector database (embedded)
- Hybrid search (BM25 + vector + RRF)
- LLM provider abstraction (Anthropic, OpenAI, Google, Custom)
- Agentic RAG controller (planner, evaluator, critic)
- GPTCache semantic caching
- Arize Phoenix tracing
- Ragas evaluation
- File system auto-watch
- REST API endpoints

**Frontend (React + TypeScript)**:
- Chat interface with citations
- Document management
- Collection management
- Settings (providers, embeddings)
- API service layer

**Desktop (Tauri)**:
- Native window
- Python sidecar management
- Cross-platform packaging

**Documentation**:
- User guide
- Installation guide
- Troubleshooting guide
- Architecture documentation
- API reference
- Development guide

**Total tasks**: 37
**Estimated time**: 40-60 hours for experienced developer

## Next Steps

1. Review this plan
2. Execute tasks in order (use subagent-driven-development)
3. Run end-to-end verification
4. Package for distribution
5. Share with users

Good luck! 🚀