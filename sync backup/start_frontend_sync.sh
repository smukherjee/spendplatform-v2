#!/bin/bash

# Script to start Frontend server configured for SYNC backend
# This script ensures frontend is connected to the traditional sync backend (port 8000)
# Optimized for: Compatibility, simple debugging, traditional development

echo "🚀 Starting Frontend for SYNC Backend Connection"
echo "🐌 Connecting to traditional sync backend (port 8000)"
echo "🔗 Features: Standard sync I/O, basic endpoints, simple debugging"
echo ""

# Get the directory where this script is located (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if frontend directory exists
if [ ! -d "$SCRIPT_DIR/frontend" ]; then
    echo "❌ Frontend directory not found at $SCRIPT_DIR/frontend"
    echo "📝 Please create the frontend directory first"
    exit 1
fi

# Navigate to frontend directory
cd "$SCRIPT_DIR/frontend"

# Kill any existing frontend servers
echo "🔄 Stopping any existing frontend servers..."
pkill -f "node.*vite" 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true
pkill -f "next" 2>/dev/null || true

# Wait for processes to stop
sleep 2

# Configure environment for sync backend
echo "🔧 Configuring frontend for SYNC backend..."
if [ -f ".env.sync" ]; then
    cp .env.sync .env
    echo "✅ Copied .env.sync to .env"
else
    echo "⚠️  .env.sync not found, creating default sync configuration..."
    cat > .env << 'EOF'
# Frontend Configuration for SYNC Backend
# Traditional sync server for compatibility and simple debugging

REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_BACKEND_TYPE=sync
REACT_APP_PERFORMANCE_MODE=standard
REACT_APP_CACHE_ENABLED=false
REACT_APP_REDIS_ENABLED=false

# Development settings
REACT_APP_ENV=development
REACT_APP_DEBUG=true
REACT_APP_LOG_LEVEL=info

# API Configuration
REACT_APP_TIMEOUT=15000
REACT_APP_RETRY_ATTEMPTS=2
REACT_APP_CONCURRENT_REQUESTS=5

# Basic features for sync backend
REACT_APP_REAL_TIME_UPDATES=false
REACT_APP_BATCH_OPERATIONS=false
REACT_APP_ADVANCED_FILTERING=false
EOF
    echo "✅ Created default sync configuration"
fi

# Check for node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Verify backend connectivity
echo "🔍 Checking sync backend connectivity..."
if curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
    echo "✅ Sync backend is running and accessible"
else
    echo "⚠️  Sync backend not detected at http://localhost:8000"
    echo "📝 Make sure to start the sync backend first:"
    echo "   ./start_backend_sync.sh"
    echo ""
    echo "🔄 Frontend will start anyway and connect when backend is available"
fi

# Determine development script
DEV_SCRIPT=""
if grep -q '"dev"' package.json; then
    DEV_SCRIPT="dev"
elif grep -q '"start"' package.json; then
    DEV_SCRIPT="start"
elif grep -q '"serve"' package.json; then
    DEV_SCRIPT="serve"
else
    echo "❌ No development script found in package.json"
    exit 1
fi

echo ""
echo "🚀 Starting frontend development server..."
echo "📊 Configuration: SYNC Backend (Traditional)"
echo "🔗 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "💚 Health Check: http://localhost:8000/health"
echo ""
echo "🌐 Frontend will be available at:"
echo "   📱 Next.js: http://localhost:3000"
echo "   ⚛️  React (CRA): http://localhost:3000"
echo "   ⚡ Vite: http://localhost:5173"
echo ""
echo "🛠️  Development Features:"
echo "   🐌 Traditional sync I/O"
echo "   🔍 Simple debugging"
echo "   🔧 Basic endpoint compatibility"
echo "   📝 Standard logging"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the frontend development server
npm run $DEV_SCRIPT