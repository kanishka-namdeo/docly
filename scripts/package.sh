#!/bin/bash
# Package the complete Doc Assistant application

set -e

echo "========================================="
echo "Packaging Doc Assistant"
echo "========================================="

# Build backend
echo ""
echo "Step 1/3: Building backend..."
echo "-----------------------------------------"
./scripts/build_backend.sh

# Build frontend
echo ""
echo "Step 2/3: Building frontend..."
echo "-----------------------------------------"
./scripts/build_frontend.sh

# Build Tauri app
echo ""
echo "Step 3/3: Building Tauri desktop app..."
echo "-----------------------------------------"
cd src-tauri

# Check if Rust dependencies are installed
if [ ! -d "target" ]; then
    echo "Installing Rust dependencies..."
    cargo build --release
fi

# Build the Tauri app
echo "Building Tauri application..."
cargo tauri build

echo ""
echo "========================================="
echo "Package created successfully!"
echo "========================================="
echo "Output location: src-tauri/target/release/bundle/"
echo ""
echo "Bundle contents:"
ls -lh src-tauri/target/release/bundle/ 2>/dev/null || echo "Bundle directory not found"
