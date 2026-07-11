# Frontend Source Code

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
- `index.css` — Global styles (Tailwind directives, shadcn CSS variables, scrollbar styling, focus styles)

## Local Contracts

### Pages
- `Chat.tsx` — Main chat interface with conversation management, collection scoping (dropdown to target queries to specific collections), setup validation (blocks new chat if LM Studio disconnected or no provider), and inline conversation rename
- `Documents.tsx` — Document and collection management with two-panel layout
- `Settings.tsx` — Provider and embedding configuration via shadcn Tabs component (Model, Embedding, Preferences)

### Components
Organized by feature domain in `components/`:

#### Chat/
- `AssistantChatView.tsx` — Chat message display and input with typing indicator via `thread.isRunning`, citation cards using shadcn Card

#### Documents/
- `CollectionList.tsx` — List and manage document collections with Dialog for create/rename, AlertDialog for delete confirmation, ScrollArea for overflow
- `DocumentList.tsx` — List and manage documents within collections with auto-polling every 3s for pending documents, Badge for status indicators

#### Settings/
- `ModelConfig.tsx` — LLM provider configuration with Card containers, shadcn Button/Input/Select/Label, lucide icons for actions
- `EmbeddingConfig.tsx` — Embedding model configuration with Card, Button, Select, Label
- `PreferencesConfig.tsx` — Theme and language preferences with Card, Select, Label

#### Layout/
- `Sidebar.tsx` — Navigation sidebar with Tailwind-styled links and active state highlighting

#### common/
- `ErrorBoundary.tsx` — React error boundary with user-friendly fallback using shadcn Button

### Services
- `api.ts` — API client for backend communication (base URL: http://localhost:8000) — includes conversationsApi.update() for conversation rename/scoping

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
cd frontend && npm run dev
```
Development server runs on port 1420 with hot module replacement.

### Building for Production
```bash
cd frontend && npm run build
```
Output: `frontend/dist/` with optimized and minified assets.

### Type Checking
```bash
cd frontend && npx tsc --noEmit
```

### Key Patterns
- **shadcn/ui components** for all UI primitives (Button, Input, Card, Dialog, Select, Tabs, Badge, ScrollArea, etc.)
- **Tailwind CSS utility classes** for styling — no inline `style={{}}` on UI elements (only layout containers and SVG props)
- **Light/dark theme** via `data-theme` attribute on `<html>`, using shadcn's HSL-based CSS variables
- **Toast notifications** via Sonner (`toast.success()`, `toast.error()`, `toast.loading()`)
- **Icons** from lucide-react
- **cn() utility** from `@/lib/utils` for class merging
- Flex layout with `flex-shrink-0` for fixed-width sidebars and `min-w-0` for flex children to prevent overflow

### Adding New Features
1. Define types in `types/` if needed
2. Create API methods in `services/api.ts`
3. Implement components in appropriate `components/` subdirectory using shadcn/ui primitives
4. Create or update page in `pages/`
5. Add route in `App.tsx` if new page

## Verification

- Type check: `npx tsc --noEmit`
- Build: `npm run build`
- Dev server: `npm run dev` (verify http://localhost:1420 loads)
- Dark theme: set `data-theme="dark"` on `<html>` element and verify all components use shadcn semantic colors

## Child DOX Index

- `pages/` — Page components (Chat, Documents, Settings)
- `components/` — Reusable UI components organized by feature domain
- `services/` — API service layer
- `hooks/` — Custom React hooks
- `types/` — TypeScript type definitions
- `lib/` — Utility libraries and helpers
