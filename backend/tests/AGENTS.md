# Backend Tests

## Purpose

Comprehensive test suite for the Python FastAPI backend, organized by module to ensure code quality and prevent regressions.

## Ownership

This AGENTS.md covers the `backend/tests/` directory:
- `test_api/` — API endpoint tests
- `test_database/` — Database model and repository tests
- `test_ingestion/` — Ingestion pipeline tests (parsers, chunker, embedder, indexer)
- `test_retrieval/` — Retrieval and search tests
- `test_llm/` — LLM provider tests
- `test_agentic/` — Agentic RAG orchestration tests
- `integration/` — End-to-end integration tests
- `__init__.py` — Test package initialization

## Local Contracts

### Test Organization
- Tests mirror the application structure in `app/`
- Each module has corresponding test directory
- Integration tests verify cross-module interactions

### Test Patterns
- pytest as test framework
- Async tests using pytest-asyncio
- Fixtures for common setup (database sessions, test data)
- Mocking external services (LLM providers, Qdrant)

### Running Tests
```bash
cd backend
venv/Scripts/python.exe -m pytest tests/ -v
```

### Test Coverage Areas
- API endpoints: Request/response validation, error handling
- Database: Model validation, repository operations
- Ingestion: Parser functionality, chunking logic, embedding integration
- Retrieval: Vector search, hybrid search, result ranking
- LLM: Provider adapters, response parsing
- Agentic: Planner, evaluator, critic, controller logic
- Integration: Full pipeline workflows

## Work Guidance

### Writing Tests
1. Place test in appropriate module directory
2. Use descriptive test names explaining the behavior
3. Follow Arrange-Act-Assert pattern
4. Use fixtures for common setup
5. Mock external dependencies

### Test Naming Convention
```python
def test_<what_is_being_tested>_<scenario>_<expected_outcome>():
```

### Fixtures
- Use pytest fixtures for reusable setup
- Database fixtures should use test database
- Clean up resources in teardown

### Running Specific Tests
```bash
# Run specific test file
venv/Scripts/python.exe -m pytest tests/test_api/test_collections.py -v

# Run tests matching pattern
venv/Scripts/python.exe -m pytest tests/ -k "test_create" -v
```

## Verification

- Full test suite: `venv/Scripts/python.exe -m pytest tests/ -v`
- Test with coverage: `venv/Scripts/python.exe -m pytest tests/ --cov=app`
- Run specific module: `venv/Scripts/python.exe -m pytest tests/test_<module>/ -v`

## Child DOX Index

- `test_api/` — API endpoint tests
- `test_database/` — Database model and repository tests
- `test_ingestion/` — Ingestion pipeline tests
- `test_retrieval/` — Retrieval and search tests
- `test_llm/` — LLM provider tests
- `test_agentic/` — Agentic RAG tests
- `integration/` — End-to-end integration tests
