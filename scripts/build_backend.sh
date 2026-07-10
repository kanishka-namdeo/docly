#!/bin/bash
# Build backend for production

set -e

echo "Building backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    source venv/Scripts/activate
fi

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "Running tests..."
pytest tests/ -v

# Build with PyInstaller
echo "Building executable..."
pip install pyinstaller
pyinstaller --onefile --name backend app/main.py

echo "Backend built successfully"
echo "Binary location: backend/dist/backend"
