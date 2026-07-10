# Backend API Routes

## Purpose

REST API endpoint implementations for the FastAPI backend, handling HTTP requests and delegating to business logic layers.

## Ownership

This AGENTS.md covers the `backend/app/api/routes/` directory:
- Route handlers for all API endpoints
- Request validation and response formatting
- Error handling and HTTP status codes

## Local Contracts

### API Endpoints
- `/collections` — Collection CRUD operations (create, read, update, delete)
- `/documents` — Document management and indexing operations
- `/conversations` — Conversation history management
- `/chat` — Chat endpoint with agentic RAG integration
- `/settings` — Provider and embedding configuration
- `/health` — Health check endpoint

### Route Patterns
- Each route module corresponds to a resource
- Use FastAPI dependency injection for services
- Return Pydantic models for response validation
- Handle errors with appropriate HTTP status codes

## Work Guidance

### Adding New Routes
1. Create route handler function with appropriate HTTP method decorator
2. Define request/response schemas in `schemas/`
3. Inject dependencies (repositories, services) via FastAPI
4. Validate input and handle errors
5. Return properly typed responses

### Route Structure
```python
@router.get("/items")
async def get_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> List[Item]:
    # Implementation
```

### Error Handling
- Use HTTPException for client errors (4xx)
- Log server errors (5xx) with context
- Return consistent error response format

## Verification

- Test endpoints with curl or Postman
- Verify request/response schemas match documentation
- Check error handling for edge cases
- Run API tests: `pytest tests/test_api/ -v`

## Child DOX Index

All routes are defined in this directory. No further nesting required.
