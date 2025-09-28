#!/bin/bash

# Script to run FastAPI server from project root directory
# This script navigates to the backend/src directory and starts the server

# Get the directory where this script is located (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Kill any existing uvicorn/FastAPI servers
echo "Stopping any existing backend servers..."
pkill -f uvicorn 2>/dev/null || true
pkill -f "python.*main:app" 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Navigate to backend/src directory
cd "$SCRIPT_DIR/backend/src"

# Activate virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

echo "Starting FastAPI backend server on http://0.0.0.0:8000"
# Start the FastAPI server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000