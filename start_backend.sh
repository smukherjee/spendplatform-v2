#!/bin/bash

# Script to run ASYNC FastAPI server from project root directory
# This script starts the high-performance async server with Redis caching on port 8001

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
    echo "📝 Please ensure the backend main file exists"
    exit 1
fi

# Check Redis connection (optional warning)
echo "🔍 Checking Redis connection..."
if command -v redis-cli >/dev/null 2>&1; then
    if redis-cli ping >/dev/null 2>&1; then
        echo "✅ Redis is running - caching enabled"
    else
        echo "⚠️ Redis not running - caching will be disabled"
        echo "📝 To start Redis: brew services start redis (macOS) or sudo systemctl start redis (Linux)"
    fi
else
    echo "⚠️ Redis CLI not found - caching status unknown"
fi

echo ""
echo "🚀 Starting FastAPI backend server"
echo "⚡ High-performance server with Redis caching"
echo "🌐 Server URL: http://0.0.0.0:8001"
echo "📊 Health Check: http://0.0.0.0:8001/health"
echo "📖 API Docs: http://0.0.0.0:8001/docs"
echo "🔧 Features: Async I/O, Redis caching, performance monitoring"
echo "🔐 Test credentials: superadmin/superadmin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001