# Frontend - React 18 + TypeScript

React 18 single-page application providing the user interface for document management, chat interactions, and settings configuration.

## Ownership

The `frontend/` directory contains the React SPA. See `src/AGENTS.md` for source-level details.

## Work Guidance

### Running the App
```bash
cd frontend && npm run dev
```
Development server runs on port 1420.

### Building
```bash
cd frontend && npm run build
```

### Type Checking
```bash
cd frontend && npx tsc --noEmit
```

### Key Conventions
- shadcn/ui components for all UI primitives (Button, Input, Card, Dialog, Select, Tabs, etc.)
- Tailwind CSS utility classes for styling — no inline `style={{}}` on UI elements
- Light/dark theme via `data-theme` attribute, using shadcn's HSL-based CSS variables
- Toast notifications via Sonner (`toast.success()`, `toast.error()`)
- Icons from lucide-react
- `cn()` utility from `@/lib/utils` for class merging

### Verification
- `npx tsc --noEmit` — zero TypeScript errors
- `npm run build` — successful production build

## Child DOX Index

- **src/** — React application source code (pages, components, services, hooks, types, lib). See `src/AGENTS.md` for component-level contracts.
