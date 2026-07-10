# Frontend Source Code

## Purpose

React 18 + TypeScript application source code, including pages, components, services, hooks, types, and utilities.

## Ownership

This AGENTS.md covers the `frontend/src/` directory:
- `pages/` — Page components (Chat, Documents, Settings)
- `components/` — Reusable UI components organized by feature
- `services/` — API service layer for backend communication
- `hooks/` — Custom React hooks
- `types/` — TypeScript type definitions
- `lib/` — Utility libraries and helpers
- `App.tsx` — Root application component with routing
- `main.tsx` — Application entry point

## Local Contracts

### Pages
- `Chat.tsx` — Main chat interface with conversation management
- `Documents.tsx` — Document and collection management
- `Settings.tsx` — Provider and embedding configuration

### Components
Organized by feature domain in `components/`:
- `Chat/` — Chat interface components
- `Documents/` — Document and collection management
- `Settings/` — Configuration components
- `Layout/` — Layout and navigation components

### Services
- `api.ts` — API client for backend communication (base URL: http://localhost:8000)

### Types
- `index.ts` — TypeScript type definitions for all entities (Collection, Document, Conversation, Message, ProviderConfig, etc.)

### Application Structure
- React Router for client-side routing
- Functional components with hooks
- TypeScript for type safety
- Service layer for API communication

## Work Guidance

### Running the Application
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

### Adding New Features
1. Define types in `types/` if needed
2. Create API methods in `services/api.ts`
3. Implement components in appropriate `components/` subdirectory
4. Create or update page in `pages/`
5. Add route in `App.tsx` if new page

## Verification

- Type check: `npm run type-check`
- Lint: `npm run lint`
- Build: `npm run build`
- Dev server: `npm run dev` (verify http://localhost:1420 loads)

## Child DOX Index

- `pages/` — Page components (Chat, Documents, Settings)
- `components/` — Reusable UI components organized by feature domain
- `services/` — API service layer
- `hooks/` — Custom React hooks
- `types/` — TypeScript type definitions
- `lib/` — Utility libraries and helpers
