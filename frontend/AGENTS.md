# Frontend - React 18 + TypeScript

## Purpose

React 18 single-page application with TypeScript, providing the user interface for document management, chat interactions, and settings configuration.

## Ownership

This AGENTS.md covers the `frontend/` directory:
- `src/pages/` — Page components (Chat, Documents, Settings)
- `src/components/` — Reusable UI components
  - `Chat/` — Chat interface components
  - `Documents/` — Document and collection management components
  - `Settings/` — Configuration components
  - `Layout/` — Layout components (Sidebar)
- `src/services/` — API service layer
- `src/hooks/` — Custom React hooks
- `src/types/` — TypeScript type definitions
- `src/lib/` — Utility libraries

## Local Contracts

### Pages
- `Chat.tsx` — Main chat interface with conversation management
- `Documents.tsx` — Document and collection management
- `Settings.tsx` — Provider and embedding configuration

### Components
- `AssistantChatView.tsx` — Chat message display and input
- `CollectionList.tsx` — List and manage document collections
- `DocumentList.tsx` — List and manage documents within collections
- `ModelConfig.tsx` — LLM provider configuration
- `EmbeddingConfig.tsx` — Embedding model configuration
- `Sidebar.tsx` — Navigation sidebar

### Services
- `api.ts` — API client for backend communication (base URL: http://localhost:8000)

### Types
- `index.ts` — TypeScript type definitions for all entities

## Work Guidance

### Running the Frontend
```bash
cd frontend
npm run dev
```
Development server runs on port 1420 with hot module replacement.

### Building for Production
```bash
cd frontend
npm run build
```
Output: `frontend/dist/` with optimized and minified assets.

### Type Checking
```bash
cd frontend
npm run type-check
```

### Linting
```bash
cd frontend
npm run lint
```

### Key Patterns
- Functional components with hooks
- TypeScript for type safety
- Service layer for API communication
- React Router for client-side routing
- Inline styles (current approach)

## Verification

- Type check: `npm run type-check`
- Lint: `npm run lint`
- Build: `npm run build`
- Dev server: `npm run dev` (verify http://localhost:1420 loads)

## Child DOX Index

- **src/** — React application source code (pages, components, services, hooks, types, lib)
