#!/bin/bash
# Unified development startup - starts backend, frontend, and Tauri desktop
# Usage: ./scripts/run_dev.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down services..."
    [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
    [ -n "$TAURI_PID" ] && kill $TAURI_PID 2>/dev/null || true
    echo "All services stopped."
    exit 0
}

# Trap Ctrl+C
trap cleanup EXIT INT TERM

echo "========================================="
echo "Starting Doc Assistant Development"
echo "========================================="
echo ""

# Check prerequisites
if ! command -v npm &> /dev/null; then
    echo "ERROR: Node.js is not installed."
    exit 1
fi

if ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed."
    exit 1
fi

if ! command -v cargo &> /dev/null; then
    echo "ERROR: Rust/Cargo is not installed. Install from https://rustup.rs/"
    exit 1
fi

# Start backend if not already running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "Starting backend..."
    cd "$PROJECT_ROOT/backend"
    
    # Activate virtual environment if exists
    if [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    elif [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
    
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
    BACKEND_PID=$!
    cd "$PROJECT_ROOT"
    
    # Wait for backend to be ready
    echo "Waiting for backend to start..."
    for i in $(seq 1 30); do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✓ Backend ready (PID: $BACKEND_PID)"
            break
        fi
        sleep 1
    done
else
    echo "✓ Backend already running"
fi

echo ""
echo "Starting Tauri desktop app..."
cd "$PROJECT_ROOT/src-tauri"

# Build frontend if needed (Tauri's beforeDevCommand will handle this, but ensure dist exists)
if [ ! -d "../frontend/dist" ]; then
    echo "Building frontend for Tauri..."
    cd ../frontend
    npm run build
    cd ../src-tauri
fi

# Start Tauri (this will also start the frontend dev server via beforeDevCommand)
cargo tauri dev