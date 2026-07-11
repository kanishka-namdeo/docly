# Backend - Python FastAPI

## Purpose

Python FastAPI backend providing REST API endpoints, document ingestion pipeline, vector search, LLM integration, and agentic RAG orchestration.

## Ownership

This AGENTS.md covers the `backend/` directory:
- `app/` — Main application code
  - `api/routes/` — REST API endpoints
  - `database/` — SQLAlchemy models and repositories
  - `ingestion/` — Document parsing, chunking, embedding, indexing
  - `retrieval/` — Qdrant vector search and hybrid retrieval
  - `agentic/` — Agentic RAG orchestration (planner, evaluator, critic, controller)
  - `llm/` — LLM client and provider implementations
  - `cache/` — GPTCache semantic caching
  - `tracing/` — Arize Phoenix observability
  - `evaluation/` — Ragas RAG quality metrics
  - `schemas/` — Pydantic request/response models
- `tests/` — Test suite organized by module
- `venv/` — Python virtual environment (excluded from version control)

## Local Contracts

### API Routes
- `/collections` — Collection CRUD operations
- `/documents` — Document management and indexing
- `/conversations` — Conversation history management
- `PUT /conversations/{id}` — Update conversation title or collection scope
- `/chat` — Chat endpoint with agentic RAG
- `/settings` — Provider and embedding configuration
- `/health` — Health check endpoint

### Database Models
- `Collection` — Document collection with name and description
- `Document` — Individual document with status tracking (pending, processing, indexed, error)
- `Conversation` — Chat conversation with optional collection scope
- `Message` — Individual message with role, content, and citations
- `ProviderConfig` — LLM provider configuration

### Ingestion Pipeline
```
File → Parser → Chunker → Embedder → Qdrant + SQLite
```

Supported parsers: PDF, DOCX, XLSX, Markdown, HTML

### Agentic RAG Flow
```
Query → Planner → Retrieve → Evaluate → Critic → Iterate → Response
```

### Configuration
- Port: 8000
- Database: SQLite (default: `backend.db`)
- Qdrant: Embedded mode
- Embeddings: LM Studio on port 1234
- CORS: All origins allowed (development)

## Work Guidance

### Running the Backend
```bash
cd backend
venv/Scripts/python.exe -m uvicorn app.main:app --reload
```

### Running Tests
```bash
cd backend
venv/Scripts/python.exe -m pytest tests/ -v
```

### Test Organization
- `test_api/` — API endpoint tests
- `test_database/` — Database model and repository tests
- `test_ingestion/` — Ingestion pipeline tests
- `test_retrieval/` — Retrieval tests
- `test_llm/` — LLM provider tests
- `test_agentic/` — Agentic RAG tests
- `integration/` — End-to-end integration tests

### Key Patterns
- Repository pattern for data access
- Dependency injection via FastAPI
- Async/await throughout
- Pydantic schemas for validation
- SQLAlchemy ORM for database

## Verification

- Run full test suite: `venv/Scripts/python.exe -m pytest tests/ -v`
- Check for import errors: `venv/Scripts/python.exe -c "from app.main import app"`
- Verify API health: `curl http://localhost:8000/health`

## Child DOX Index

- **app/** — Core application code (API routes, database, ingestion, retrieval, agentic RAG, LLM, cache, tracing, evaluation, schemas)
- **tests/** — Test suite organized by module (API, database, ingestion, retrieval, LLM, agentic, integration)
