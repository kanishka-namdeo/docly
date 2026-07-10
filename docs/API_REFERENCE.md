# API Reference

## Base URL

```
http://127.0.0.1:8000
```

## Authentication

No authentication required (local application).

## Endpoints

### Collections

#### List Collections
```http
GET /collections/
```

**Response**:
```json
[
  {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  }
]
```

#### Create Collection
```http
POST /collections/
Content-Type: application/json

{
  "name": "string",
  "description": "string" (optional)
}
```

**Response**: Collection object

#### Get Collection
```http
GET /collections/{collection_id}
```

**Response**: Collection object

#### Update Collection
```http
PUT /collections/{collection_id}
Content-Type: application/json

{
  "name": "string" (optional),
  "description": "string" (optional)
}
```

**Response**: Collection object

#### Delete Collection
```http
DELETE /collections/{collection_id}
```

**Response**:
```json
{
  "status": "deleted"
}
```

---

### Documents

#### List Documents
```http
GET /documents/collection/{collection_id}
```

**Response**:
```json
[
  {
    "id": "uuid",
    "collection_id": "uuid",
    "file_path": "string",
    "file_type": "string",
    "file_size": 12345,
    "status": "pending|indexed|error",
    "error_message": "string" (optional),
    "created_at": "ISO8601",
    "updated_at": "ISO8601",
    "indexed_at": "ISO8601" (optional)
  }
]
```

#### Upload Document
```http
POST /documents/upload?collection_id={collection_id}
Content-Type: multipart/form-data

file: <binary file data>
```

**Supported formats**: PDF, DOCX, XLSX, MD, HTML

**Response**:
```json
{
  "document_id": "uuid",
  "status": "success|error",
  "chunks_indexed": 42
}
```

#### Delete Document
```http
DELETE /documents/{document_id}
```

**Response**:
```json
{
  "status": "deleted"
}
```

---

### Conversations

#### List Conversations
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
