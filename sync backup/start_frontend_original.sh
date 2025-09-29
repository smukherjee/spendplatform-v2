#!/bin/bash

# Script to run Frontend server from project root directory
# UPDATED: Now supports async/sync backend server switching
# This script navigates to the frontend directory and starts the development server

# Get the directory where this script is located (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check frontend server type preference
FRONTEND_BACKEND_TYPE="${FRONTEND_BACKEND_TYPE:-async}"
if [ "$1" = "sync" ]; then
    FRONTEND_BACKEND_TYPE="sync"
elif [ "$1" = "async" ]; then
    FRONTEND_BACKEND_TYPE="async"
fi

echo "🔧 Frontend Backend Connection: $FRONTEND_BACKEND_TYPE"
if [ "$FRONTEND_BACKEND_TYPE" = "async" ]; then
    echo "⚡ Connecting to high-performance async backend (port 8001)"
    echo "🔗 Features: Redis caching, async I/O, performance monitoring"
else
    echo "🐌 Connecting to traditional sync backend (port 8000)"
    echo "🔗 Features: Standard sync I/O, basic endpoints, simple debugging"
fi
echo ""

# Kill any existing Node.js/React dev servers
echo "🔄 Stopping any existing frontend servers..."
pkill -f "node.*vite" 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true
pkill -f "next" 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Check if frontend directory exists
if [ ! -d "$SCRIPT_DIR/frontend" ]; then
    echo "❌ Frontend directory not found at $SCRIPT_DIR/frontend"
    echo "📝 To set up a frontend application:"
    echo ""
    echo "   Option 1: Next.js (Recommended)"
    echo "   npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias '@/*'"
    echo ""
    echo "   Option 2: React with Vite"
    echo "   npm create vite@latest frontend -- --template react-ts"
    echo ""
    echo "   Option 3: Create React App"
    echo "   npx create-react-app frontend --template typescript"
    echo ""
    echo "   After creating the frontend, you can run this script again."
    exit 1
fi

# Navigate to frontend directory
cd "$SCRIPT_DIR/frontend"

# Configure environment based on backend type
echo "🔧 Configuring frontend for $FRONTEND_BACKEND_TYPE backend..."
if [ "$FRONTEND_BACKEND_TYPE" = "async" ]; then
    if [ -f ".env.async" ]; then
        cp .env.async .env
        echo "✅ Configured for async backend (port 8001)"
    else
        echo "⚠️  .env.async not found, using default configuration"
    fi
else
    if [ -f ".env.sync" ]; then
        cp .env.sync .env
        echo "✅ Configured for sync backend (port 8000)"
    else
        echo "⚠️  .env.sync not found, using default configuration"
    fi
fi

# Verify backend connectivity
echo "🔍 Checking backend connectivity..."
if [ "$FRONTEND_BACKEND_TYPE" = "async" ]; then
    if curl -s "http://localhost:8001/health" > /dev/null 2>&1; then
        echo "✅ Async backend is running and accessible"
    else
        echo "⚠️  Async backend not detected at http://localhost:8001"
        echo "📝 Start the async backend first: ./start_backend_async.sh"
    fi
else
    if curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
        echo "✅ Sync backend is running and accessible"
    else
        echo "⚠️  Sync backend not detected at http://localhost:8000"
        echo "📝 Start the sync backend first: ./start_backend_sync.sh"
    fi
fi
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Check for package.json and dev script
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found in frontend directory"
    exit 1
fi

# Determine which script to use (dev, start, or serve)
DEV_SCRIPT=""
if grep -q '"dev"' package.json; then
    DEV_SCRIPT="dev"
elif grep -q '"start"' package.json; then
    DEV_SCRIPT="start"
elif grep -q '"serve"' package.json; then
    DEV_SCRIPT="serve"
else
    echo "❌ No development script found in package.json"
    echo "📝 Please add a development script to your package.json, for example:"
    echo '   "scripts": { "dev": "next dev" }     # For Next.js'
    echo '   "scripts": { "start": "react-scripts start" }  # For Create React App'
    echo '   "scripts": { "dev": "vite" }         # For Vite'
    exit 1
fi

echo "🚀 Starting frontend development server..."
echo "📊 Configuration: $FRONTEND_BACKEND_TYPE Backend"
if [ "$FRONTEND_BACKEND_TYPE" = "async" ]; then
    echo "🔗 Backend API: http://localhost:8001"
    echo "📖 API Docs: http://localhost:8001/docs"
    echo "💚 Health Check: http://localhost:8001/health"
else
    echo "🔗 Backend API: http://localhost:8000"
    echo "📖 API Docs: http://localhost:8000/docs"
    echo "� Health Check: http://localhost:8000/health"
fi
echo ""
echo "🌐 Frontend will be available at:"
echo "   📱 Next.js: http://localhost:3000"
echo "   ⚛️  React (CRA): http://localhost:3000"
echo "   ⚡ Vite: http://localhost:5173"
echo ""
echo "💡 Usage:"
echo "   ./start_frontend.sh        # Connect to async backend (default)"
echo "   ./start_frontend.sh async  # Connect to async backend"
echo "   ./start_frontend.sh sync   # Connect to sync backend"
echo ""
echo "Press Ctrl+C to stop the server"

# Start the frontend development server
npm run $DEV_SCRIPT