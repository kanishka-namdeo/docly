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
