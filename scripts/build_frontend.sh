#!/bin/bash
# Build frontend for production

set -e

echo "Building frontend..."
cd frontend

# Install dependencies
echo "Installing dependencies..."
npm install

# Run TypeScript type check
echo "Running type check..."
npx tsc --noEmit

# Build for production
echo "Building..."
npm run build

echo "Frontend built successfully"
echo "Output location: frontend/dist/"
