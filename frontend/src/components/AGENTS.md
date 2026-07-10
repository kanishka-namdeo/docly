# Frontend Components

## Purpose

Reusable React components organized by feature domain, providing the UI building blocks for the application's pages.

## Ownership

This AGENTS.md covers the `frontend/src/components/` directory:
- `Chat/` — Chat interface components
- `Documents/` — Document and collection management components
- `Settings/` — Configuration components
- `Layout/` — Layout and navigation components

## Local Contracts

### Chat Components
- `AssistantChatView.tsx` — Main chat interface displaying messages and handling user input

### Documents Components
- `CollectionList.tsx` — List and manage document collections
- `DocumentList.tsx` — List and manage documents within collections

### Settings Components
- `ModelConfig.tsx` — LLM provider configuration (Anthropic, OpenAI, Google, Custom)
- `EmbeddingConfig.tsx` — Embedding model configuration (LM Studio)

### Layout Components
- `Sidebar.tsx` — Navigation sidebar with links to Chat, Documents, and Settings pages

## Work Guidance

### Component Structure
- Functional components with TypeScript
- Props interfaces defined inline or in separate types
- Inline styles (current approach)
- Hooks for state management and side effects

### Adding New Components
1. Create component file in appropriate feature directory
2. Define TypeScript interfaces for props
3. Implement component logic and rendering
4. Export component for use in pages

### Styling
- Current approach: inline styles
- Consider extracting common styles to shared utilities
- Maintain consistency with existing component patterns

## Verification

- Type check: `npm run type-check`
- Lint: `npm run lint`
- Visual verification: Run dev server and test component rendering

## Child DOX Index

- `Chat/` — Chat interface components (AssistantChatView)
- `Documents/` — Document and collection management (CollectionList, DocumentList)
- `Settings/` — Configuration components (ModelConfig, EmbeddingConfig)
- `Layout/` — Layout components (Sidebar)
