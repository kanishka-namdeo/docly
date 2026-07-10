# Doc Assistant - Local RAG Assistant

## Overview

A local-first desktop RAG assistant with agentic retrieval that enables users to chat with their documents using cloud LLMs. Built with Tauri 2.x, React 18, and Python FastAPI.

## Architecture

- **Frontend**: React 18 + TypeScript + Vite (port 1420)
- **Backend**: Python FastAPI (port 8000)
- **Desktop**: Tauri 2.x with Python sidecar
- **Vector DB**: Qdrant (embedded)
- **Embeddings**: LM Studio (local, port 1234)
- **LLM**: Cloud providers (Anthropic, OpenAI, Google) or custom OpenAI-compatible endpoints

## Project Structure

- **backend/** — Python FastAPI backend
  - Database models (SQLAlchemy) for collections, documents, conversations, messages, providers
  - Document ingestion: parsers (PDF, DOCX, XLSX, MD, HTML), chunker, embedder, indexer
  - Retrieval: Qdrant vector database client, hybrid search
  - LLM providers: Anthropic, OpenAI, Google, Custom (OpenAI-compatible)
  - Agentic RAG: planner, evaluator, critic, controller with iteration loop
  - Production: GPTCache semantic cache, Arize Phoenix tracing, Ragas evaluation
  - API routes: collections, documents, conversations, chat, settings
  - File watcher: auto-indexing with debouncing
  - Virtual environment: `backend/venv/` (Python 3.11+)
  - Run: `cd backend && venv/Scripts/python.exe -m uvicorn app.main:app --reload`
  - Test: `cd backend && venv/Scripts/python.exe -m pytest tests/ -v`

- **frontend/** — React 18 + TypeScript + Vite frontend
  - Pages: Chat, Documents, Settings
  - Components: Sidebar, ChatWindow, MessageList, MessageInput, CitationCard, CollectionList, DocumentList, ModelConfig, EmbeddingConfig
  - API service layer for backend communication
  - TypeScript types for all entities
  - Run: `cd frontend && npm run dev` (port 1420)
  - Build: `cd frontend && npm run build`

- **src-tauri/** — Tauri 2.x desktop application
  - Rust backend with Python sidecar management
  - Commands: `start_backend`, `stop_backend`
  - Configuration: `tauri.conf.json`
  - Build: `cd src-tauri && cargo tauri build`

- **docs/** — User documentation
  - USER_GUIDE.md - Feature overview and usage
  - INSTALLATION.md - Installation instructions for all platforms
  - TROUBLESHOOTING.md - Common issues and solutions

- **scripts/** - Build and packaging scripts
  - build_backend.sh - Build Python backend with PyInstaller
  - build_frontend.sh - Build React frontend
  - package.sh - Package complete application

## Development Workflow

1. Start LM Studio with embedding model on port 1234
2. Start backend: `cd backend && venv/Scripts/python.exe -m uvicorn app.main:app --reload` (port 8000)
3. Start frontend: `cd frontend && npm run dev` (port 1420)
4. For desktop: `cd src-tauri && cargo tauri dev`

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Qdrant, httpx, anthropic, openai, google-generativeai, tenacity, watchdog
- **Frontend**: React 18, TypeScript, Vite, React Router
- **Desktop**: Tauri 2.x, Rust
- **Embeddings**: LM Studio (local, nomic-embed-text-v1.5)
- **LLM**: Cloud providers (Anthropic, OpenAI, Google) or custom OpenAI-compatible endpoints

## Child DOX Index

- **backend/** — Python FastAPI backend (DB models/repos, ingestion pipeline, Qdrant retrieval, LLM providers, agentic RAG, API routes, GPTCache, Phoenix tracing, Ragas eval, file watcher)
- **frontend/** — React 18/Vite/TypeScript SPA (chat, documents, settings pages + all component library)
- **src-tauri/** — Tauri 2.x desktop app (Rust, Python sidecar management commands)
- **docs/** — User documentation (USER_GUIDE.md, INSTALLATION.md, TROUBLESHOOTING.md)
- **docs/superpowers/** — Project plans and design specs
- **scripts/** — Build and packaging scripts (build_backend.sh, build_frontend.sh, package.sh)
