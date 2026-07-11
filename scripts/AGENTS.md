# Scripts - Build and Packaging

## Purpose

Shell scripts for building the Python backend, React frontend, and packaging the complete desktop application, as well as running the development environment.

## Ownership

This AGENTS.md covers the `scripts/` directory:
- `build_backend.sh` — Build Python backend with PyInstaller
- `build_frontend.sh` — Build React frontend for production
- `package.sh` — Package complete application
- `run_dev.sh` — Unified development startup (Unix/Linux/Mac)
- `run_dev.ps1` — Unified development startup (Windows PowerShell)

## Local Contracts

### run_dev.sh / run_dev.ps1
Unified development startup script that launches the complete Tauri application with all services:
1. Starts Python FastAPI backend (port 8000)
2. Starts frontend dev server (via Tauri's beforeDevCommand)
3. Launches Tauri desktop window

**Usage:**
```bash
# Unix/Linux/Mac
./scripts/run_dev.sh

# Windows PowerShell
.\scripts\run_dev.ps1
```

**Features:**
- Checks prerequisites (Node.js, Python, Rust)
- Waits for backend to be ready before starting Tauri
- Handles cleanup on Ctrl+C
- Builds frontend if needed before launching Tauri

### build_backend.sh
Builds the Python backend for production:
1. Creates virtual environment if needed
2. Activates virtual environment
3. Installs dependencies
4. Runs test suite
5. Builds executable with PyInstaller

Output: `backend/dist/backend` (single-file executable)

### build_frontend.sh
Builds the React frontend for production:
1. Installs npm dependencies
2. Runs production build with Vite

Output: `frontend/dist/` (optimized assets)

### package.sh
Packages the complete desktop application:
1. Builds backend executable
2. Builds frontend assets
3. Copies backend binary to Tauri resources
4. Prepares for Tauri build

## Work Guidance

### Development (Recommended)
Use the unified run script to start the complete development environment:
```bash
./scripts/run_dev.sh        # Unix/Linux/Mac
.\scripts\run_dev.ps1       # Windows PowerShell
```

This launches backend, frontend, and Tauri desktop app together.

### Build Order (for packaging)
```bash
# 1. Build backend
./scripts/build_backend.sh

# 2. Build frontend
./scripts/build_frontend.sh

# 3. Package application
./scripts/package.sh

# 4. Build Tauri installer (optional)
cd src-tauri
cargo tauri build
```

### Platform-Specific Notes
- **Windows**: Virtual environment activation uses `venv/Scripts/activate`, output is `backend.exe`
- **Linux/macOS**: Virtual environment activation uses `source venv/bin/activate`, output is `backend`

## Verification

- **run_dev scripts**: Verify backend responds at http://localhost:8000/health and Tauri window opens
- Backend build: Verify `backend/dist/backend` (or `backend.exe`) exists and is executable
- Frontend build: Verify `frontend/dist/` contains optimized assets
- Package: Verify all artifacts are in place for Tauri build
- Full build: Run all three scripts in sequence and verify no errors

## Child DOX Index

No child directories with separate AGENTS.md files. All scripts are covered by this file.