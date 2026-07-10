# Scripts - Build and Packaging

## Purpose

Shell scripts for building the Python backend, React frontend, and packaging the complete desktop application.

## Ownership

This AGENTS.md covers the `scripts/` directory:
- `build_backend.sh` — Build Python backend with PyInstaller
- `build_frontend.sh` — Build React frontend for production
- `package.sh` — Package complete application

## Local Contracts

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

### Build Order
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

- Backend build: Verify `backend/dist/backend` (or `backend.exe`) exists and is executable
- Frontend build: Verify `frontend/dist/` contains optimized assets
- Package: Verify all artifacts are in place for Tauri build
- Full build: Run all three scripts in sequence and verify no errors

## Child DOX Index

No child directories with separate AGENTS.md files. All scripts are covered by this file.
