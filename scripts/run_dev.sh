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
    if [ -n "$BACKEND_PID" ]; then
        # Kill backend process group
        PGID=$(ps -o pgid= $BACKEND_PID 2>/dev/null | grep -o '[0-9]*' || true)
        [ -n "$PGID" ] && kill -- -$PGID 2>/dev/null || kill $BACKEND_PID 2>/dev/null || true
    fi
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
    # Wait for backend to be ready
    echo "Waiting for backend to start..."
    BACKEND_READY=false
    for i in $(seq 1 30); do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✓ Backend ready (PID: $BACKEND_PID)"
            BACKEND_READY=true
            break
        fi
        sleep 1
    done
    
    if [ "$BACKEND_READY" = false ]; then
        echo "ERROR: Backend failed to start within 30 seconds"
        exit 1
    fi
else
    echo "✓ Backend already running"
fi

# Start Frontend Dev Server
echo ""
echo "Starting Frontend Dev Server..."
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!
cd "$PROJECT_ROOT"

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
FRONTEND_READY=false
for i in $(seq 1 30); do
    if curl -s http://localhost:1420 > /dev/null 2>&1; then
        echo "✓ Frontend ready (PID: $FRONTEND_PID)"
        FRONTEND_READY=true
        break
    fi
    sleep 1
done

if [ "$FRONTEND_READY" = false ]; then
    echo "ERROR: Frontend failed to start within 30 seconds"
    exit 1
fi

echo ""
echo "Starting Tauri desktop app..."
cd "$PROJECT_ROOT/src-tauri"

# Start Tauri
cargo tauri dev