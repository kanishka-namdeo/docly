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
  - `common/` — Shared utility components (ToastContext, ErrorBoundary)
- `src/services/` — API service layer
- `src/hooks/` — Custom React hooks
- `src/types/` — TypeScript type definitions
- `src/lib/` — Utility libraries

## Local Contracts

### Pages
- `Chat.tsx` — Chat interface with conversation management, collection scoping (dropdown to target queries to specific collections), setup validation (blocks new chat if LM Studio disconnected or no provider), and inline conversation rename
- `Documents.tsx` — Document and collection management
- `Settings.tsx` — Provider and embedding configuration

### Components
- `AssistantChatView.tsx` — Chat message display and input with typing indicator via thread.isRunning
- `CollectionList.tsx` — List and manage document collections (double-click to rename inline)
- `DocumentList.tsx` — List and manage documents within collections (auto-polls every 3s for pending documents)
- `ModelConfig.tsx` — LLM provider configuration
- `EmbeddingConfig.tsx` — Embedding model configuration
- `Sidebar.tsx` — Navigation sidebar
- `common/ToastContext.tsx` — Toast notifications (success/error/warning/info, 4s auto-dismiss)
- `common/ErrorBoundary.tsx` — React error boundary with user-friendly fallback

### Services
- `api.ts` — API client for backend communication (base URL: http://localhost:8000) — includes conversationsApi.update() for conversation rename/scoping

### Types
- `index.ts` — TypeScript type definitions for all entities

### Library
- `assistant-runtime.ts` — @assistant-ui/react adapter with collectionId support for collection-scoped retrieval

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
npx tsc --noEmit
```
No separate type-check script is defined in package.json; `npm run build` also runs `tsc` before Vite.

### Linting
No lint script is currently configured. Add one to package.json if ESLint/Prettier is set up.

### Key Patterns
- Functional components with hooks
- TypeScript for type safety
- Service layer for API communication
- React Router for client-side routing
- Inline styles (current approach)

## Verification

- Type check: `npx tsc --noEmit`
- Build: `npm run build` (runs `tsc && vite build`)
- Dev server: `npm run dev` (verify http://localhost:1420 loads)

## Child DOX Index

- **src/** — React application source code (pages, components, services, hooks, types, lib)
