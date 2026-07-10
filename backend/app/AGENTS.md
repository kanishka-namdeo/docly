# Backend Application Code

## Purpose

Core Python FastAPI application implementing the REST API, document ingestion pipeline, vector search, LLM integration, and agentic RAG orchestration.

## Ownership

This AGENTS.md covers the `backend/app/` directory:
- `main.py` — FastAPI application entry point and middleware configuration
- `config.py` — Application configuration and settings
- `api/routes/` — REST API endpoint implementations
- `database/` — SQLAlchemy models, repositories, and session management
- `ingestion/` — Document parsing, chunking, embedding, and indexing pipeline
- `retrieval/` — Qdrant vector search and hybrid retrieval
- `agentic/` — Agentic RAG orchestration (planner, evaluator, critic, controller)
- `llm/` — LLM client and provider implementations (Anthropic, OpenAI, Google, Custom)
- `cache/` — GPTCache semantic caching layer
- `tracing/` — Arize Phoenix observability and tracing
- `evaluation/` — Ragas RAG quality metrics and evaluation
- `schemas/` — Pydantic request/response models

## Local Contracts

### Application Entry Point
- `main.py` initializes FastAPI app, CORS, and includes all route modules
- Application runs on port 8000

### API Routes
- `/collections` — Collection CRUD operations
- `/documents` — Document management and indexing
- `/conversations` — Conversation history management
- `/chat` — Chat endpoint with agentic RAG
- `/settings` — Provider and embedding configuration
- `/health` — Health check endpoint

### Database Layer
- SQLAlchemy ORM with async session management
- Models: Collection, Document, Conversation, Message, ProviderConfig
- Repository pattern for data access abstraction

### Ingestion Pipeline
```
File → Parser → Chunker → Embedder → Qdrant + SQLite
```
Supported formats: PDF, DOCX, XLSX, Markdown, HTML

### Retrieval
- Qdrant vector database (embedded mode)
- Hybrid search combining vector similarity and metadata filtering

### Agentic RAG
```
Query → Planner → Retrieve → Evaluate → Critic → Iterate → Response
```
- Planner: Determines retrieval strategy
- Evaluator: Assesses retrieved context quality
- Critic: Validates response completeness
- Controller: Orchestrates iteration loop

### LLM Integration
- Multiple providers: Anthropic, OpenAI, Google, Custom (OpenAI-compatible)
- Unified client interface
- Provider-specific adapters

### Configuration
- SQLite database (default: `backend.db`)
- Qdrant embedded mode
- LM Studio embeddings on port 1234
- CORS: All origins allowed (development)

## Work Guidance

### Running the Application
```bash
cd backend
venv/Scripts/python.exe -m uvicorn app.main:app --reload
```

### Key Patterns
- Repository pattern for data access
- Dependency injection via FastAPI
- Async/await throughout
- Pydantic schemas for validation
- SQLAlchemy ORM for database

### Adding New Features
1. Define Pydantic schemas in `schemas/`
2. Implement database models and repositories in `database/`
3. Create API routes in `api/routes/`
4. Add business logic in appropriate module (ingestion, retrieval, agentic, llm)

## Verification

- Import check: `venv/Scripts/python.exe -c "from app.main import app"`
- Health endpoint: `curl http://localhost:8000/health`
- Full test suite: `venv/Scripts/python.exe -m pytest tests/ -v`

## Child DOX Index

- `api/` — REST API route implementations
- `database/` — SQLAlchemy models, repositories, session management
- `ingestion/` — Document parsing, chunking, embedding, indexing pipeline
- `retrieval/` — Qdrant vector search and hybrid retrieval
- `agentic/` — Agentic RAG orchestration components
- `llm/` — LLM client and provider implementations
- `cache/` — GPTCache semantic caching
- `tracing/` — Arize Phoenix observability
- `evaluation/` — Ragas RAG quality metrics
- `schemas/` — Pydantic request/response models
