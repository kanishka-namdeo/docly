# src-tauri - Tauri 2.x Desktop Application

## Purpose

Tauri 2.x desktop application that wraps the React frontend and manages the Python FastAPI backend as a sidecar process.

## Ownership

This AGENTS.md covers the `src-tauri/` directory:
- `src/main.rs` — Application entry point
- `src/lib.rs` — Library root
- `src/commands/` — Tauri command implementations
  - `backend.rs` — Backend process management (start/stop)
  - `mod.rs` — Command module exports
- `Cargo.toml` — Rust dependencies
- `tauri.conf.json` — Tauri configuration
- `build.rs` — Build script

## Local Contracts

### Tauri Commands
- `start_backend` — Spawns Python backend as child process (uvicorn on 127.0.0.1:8000)
- `stop_backend` — Terminates the backend child process

### Application State
```rust
pub struct BackendState {
    pub child: Mutex<Option<Child>>,
}
```

### Configuration (tauri.conf.json)
- Product Name: Doc Assistant
- Version: 0.1.0
- Window: 1200x800, resizable
- devUrl: http://localhost:1420
- frontendDist: ../frontend/dist
- beforeDevCommand: `cd frontend && npm run dev`
- beforeBuildCommand: `cd frontend && npm run build`
- Bundle identifier: com.docassistant.app

## Work Guidance

### Running in Development Mode
```bash
cd src-tauri
cargo tauri dev
```
This starts the frontend dev server (via `beforeDevCommand`), builds the Rust application, and launches the desktop window.

**Backend lifecycle:** The Python backend is NOT started automatically. The frontend calls the `start_backend` Tauri command when needed, which spawns `uvicorn app.main:app` in the `../backend` directory. Call `stop_backend` to terminate it.

### Building for Production
```bash
cd src-tauri
cargo tauri build
```
Output: Platform-specific installer in `target/release/bundle/`

### Key Patterns
- Tauri commands for IPC between frontend and Rust
- Backend managed as sidecar process
- State management via Tauri's state system
- Async command handlers

## Verification

- Development mode: `cargo tauri dev` (verify window opens and app loads)
- Production build: `cargo tauri build` (verify installer created)
- Rust compilation: `cargo check` (verify no compilation errors)

## Child DOX Index

No child directories with separate AGENTS.md files. All Tauri code is covered by this file.
