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

**Key Pages**:
- `Chat.tsx`: Main chat interface with conversation management
- `Documents.tsx`: Document and collection management
- `Settings.tsx`: Provider and embedding configuration

**Key Components**:
- `ChatWindow`: Message list and input
- `CitationCard`: Expandable source citations
- `CollectionList`: Document collection browser
- `DocumentList`: Document upload and status

### Backend (Python + FastAPI)
- **Framework**: FastAPI 0.115+
- **Database**: SQLite with SQLAlchemy ORM (async via aiosqlite)
- **Vector DB**: Qdrant (embedded mode)
- **Document Parsing**: Unstructured.io
- **LLM Clients**: anthropic, openai, google-generativeai

**Key Modules**:
- `app/api/routes/`: REST API endpoints
- `app/agentic/`: Agentic RAG logic (planner, evaluator, critic, controller)
- `app/ingestion/`: Document parsing, chunking, embedding, indexing
- `app/retrieval/`: Qdrant client and hybrid search
- `app/llm/providers/`: LLM provider implementations
- `app/database/`: SQLAlchemy models and repositories

### Agentic RAG Pipeline

```
User Query
    ↓
┌─────────────┐
│   Planner   │ → Decompose into sub-queries
└─────────────┘
    ↓
┌─────────────┐
│  Retrieval  │ → Vector search via Qdrant
└─────────────┘
    ↓
┌─────────────┐
│  Evaluator  │ → Score confidence (high/medium/low)
└─────────────┘
    ↓
┌─────────────┐
│  Generator  │ → Generate answer with citations
└─────────────┘
    ↓
┌─────────────┐
│   Critic    │ → Validate answer against sources
└─────────────┘
    ↓
┌─────────────┐
│ Controller  │ → Iterate if needed (max 5 loops)
└─────────────┘
    ↓
Final Answer with Citations
```

### Data Flow

1. **Document Ingestion**:
   ```
   Upload → Parse → Chunk → Embed → Store in Qdrant
   ```

2. **Query Processing**:
   ```
   Query → Plan → Retrieve → Evaluate → Generate → Critique → Respond
   ```

## Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Desktop framework | Tauri 2.x | Lightweight, native, Rust backend |
| Frontend | React 18 + Vite | Fast dev experience, small bundle |
| Backend | FastAPI | Async-first, auto docs, type safety |
| Vector DB | Qdrant (embedded) | No external service needed |
| Embeddings | LM Studio (local) | Privacy-first, no API costs |
| Database | SQLite + aiosqlite | Zero-config, async, portable |
| LLM | Cloud APIs | Best quality, user brings own key |
