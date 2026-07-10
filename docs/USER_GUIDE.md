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
