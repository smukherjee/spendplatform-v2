#!/bin/bash

# Script to run SYNC FastAPI server from project root directory (BACKUP)
# This script starts the traditional sync server on port 8000

# Get the directory where this script is located (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Kill any existing uvicorn/FastAPI servers
echo "🔄 Stopping any existing backend servers..."
pkill -f uvicorn 2>/dev/null || true
pkill -f "python.*main:app" 2>/dev/null || true
pkill -f "python.*main_async:app" 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Navigate to backend/src directory
cd "$SCRIPT_DIR/backend/src"

# Activate virtual environment
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
    echo "✅ Virtual environment activated"
else
    echo "⚠️ Virtual environment not found at $SCRIPT_DIR/.venv/bin/activate"
    echo "📝 Please create virtual environment first: python -m venv .venv"
fi

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found in backend/src directory"
    echo "📝 Please ensure the sync server file exists"
    exit 1
fi

echo ""
echo "🚀 Starting SYNC FastAPI backend server (BACKUP)"
echo "🐌 Traditional synchronous server"
echo "🌐 Server URL: http://0.0.0.0:8000"
echo "📊 Health Check: http://0.0.0.0:8000/health"
echo "📖 API Docs: http://0.0.0.0:8000/docs"
echo "🔧 Features: Standard sync I/O, traditional endpoints"
echo "🔐 Test credentials: user/user123 or superadmin/superadmin123"
echo ""
echo "💡 For better performance, use async server: ./start_backend_async.sh"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the SYNC FastAPI server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000