# Doc Assistant

A local-first desktop application for document Q&A using agentic RAG (Retrieval-Augmented Generation). Upload documents, ask questions, and get answers with source citations — all running locally with your choice of LLM provider.

## Features

- **Agentic RAG Pipeline**: Query decomposition, iterative retrieval, self-correction, and confidence scoring
- **Document Management**: Organize documents into collections, auto-indexing, file watching
- **Source Citations**: Every answer includes clickable citations showing exact source text
- **Multi-Provider LLM Support**: Works with OpenAI, Anthropic, Google AI, or any OpenAI-compatible API
- **Local Embeddings**: Privacy-first with LM Studio running locally
- **Desktop Native**: Lightweight Tauri app with React frontend and Python FastAPI backend

## Architecture

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

## Prerequisites

1. **LM Studio** (required for embeddings)
   - Download from https://lmstudio.ai
   - Install and launch the application
   - Download an embedding model (recommended: `nomic-embed-text-v1.5`)
   - Start the server on port 1234 (default)

2. **LLM Provider API Key** (choose one)
   - OpenAI API key (https://platform.openai.com)
   - Anthropic API key (https://console.anthropic.com)
   - Google AI API key (https://makersuite.google.com)
   - Or any OpenAI-compatible API endpoint

3. **Development Tools** (for building from source)
   - Python 3.11+
   - Node.js 18+
   - Rust (for Tauri)

## Installation

### Pre-built Installers

Download from the [releases page](https://github.com/kanishka-namdeo/docly/releases):

- **Windows**: `DocAssistant-Setup.exe`
- **macOS**: `DocAssistant.dmg`
- **Linux**: `.deb`, `.rpm`, or AUR package

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/kanishka-namdeo/docly.git
   cd docly
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Start LM Studio**
   - Launch LM Studio
   - Load an embedding model (e.g., `nomic-embed-text-v1.5`)
   - Start the server on port 1234

5. **Run in development mode**
   ```bash
   # From project root
   cargo tauri dev
   ```

6. **Build for production**
   ```bash
   cargo tauri build
   ```

## Usage

1. **Launch Doc Assistant**
2. **Configure LLM Provider**
   - Go to Settings → LLM Provider
   - Add your provider (Anthropic, OpenAI, Google, or Custom)
   - Enter your API key
3. **Verify Embeddings**
   - Go to Settings → Embeddings
   - Confirm LM Studio shows "Connected"
4. **Create a Collection**
   - Go to Documents → New Collection
   - Name your collection
5. **Upload Documents**
   - Supported formats: PDF, DOCX, XLSX, Markdown, HTML
   - Wait for indexing to complete
6. **Start Chatting**
   - Go to Chat → New Conversation
   - Ask questions about your documents
   - Answers include source citations

## Agentic RAG Pipeline

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

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Desktop Framework | Tauri 2.x (Rust) |
| Frontend | React 18 + TypeScript + Vite |
| Backend | Python FastAPI |
| Vector Database | Qdrant (embedded) |
| Embeddings | LM Studio (local) |
| Database | SQLite + SQLAlchemy |
| Document Parsing | Unstructured.io |

## Documentation

- [Installation Guide](docs/INSTALLATION.md) — Detailed setup instructions
- [User Guide](docs/USER_GUIDE.md) — Feature overview and tips
- [Architecture](docs/ARCHITECTURE.md) — System design and components
- [API Reference](docs/API_REFERENCE.md) — Backend API endpoints
- [Development Guide](docs/DEVELOPMENT.md) — Contributing and development
- [Troubleshooting](docs/TROUBLESHOOTING.md) — Common issues and solutions

## System Requirements

- **OS**: Windows 10+, macOS 10.15+, or Linux (64-bit)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB for application + document storage
- **Network**: Internet connection for LLM API calls

## License

This project is proprietary software.

## Contributing

Contributions are welcome! Please read the [Development Guide](docs/DEVELOPMENT.md) for details on how to contribute.

## Support

- **Issues**: [GitHub Issues](https://github.com/kanishka-namdeo/docly/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kanishka-namdeo/docly/discussions)
