#!/bin/bash

# Script to start Frontend server configured for ASYNC backend
# This script ensures frontend is connected to the high-performance async backend (port 8001)
# Optimized for: Redis caching, async I/O, performance monitoring

echo "🚀 Starting Frontend Server"
echo "⚡ Connecting to backend (port 8001)"
echo "🔗 Features: Redis caching, async I/O, performance monitoring"
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

# Configure environment for async backend
echo "🔧 Configuring frontend for ASYNC backend..."
if [ -f ".env.async" ]; then
    cp .env.async .env
    echo "✅ Copied .env.async to .env"
else
    echo "⚠️  .env.async not found, creating default async configuration..."
    cat > .env << 'EOF'
# Frontend Configuration for ASYNC Backend
# High-performance async server with Redis caching

REACT_APP_API_BASE_URL=http://localhost:8001
REACT_APP_BACKEND_TYPE=async
REACT_APP_PERFORMANCE_MODE=high
REACT_APP_CACHE_ENABLED=true
REACT_APP_REDIS_ENABLED=true

# Development settings
REACT_APP_ENV=development
REACT_APP_DEBUG=true
REACT_APP_LOG_LEVEL=debug

# API Configuration
REACT_APP_TIMEOUT=30000
REACT_APP_RETRY_ATTEMPTS=3
REACT_APP_CONCURRENT_REQUESTS=10

# Features enabled with async backend
REACT_APP_REAL_TIME_UPDATES=true
REACT_APP_BATCH_OPERATIONS=true
REACT_APP_ADVANCED_FILTERING=true
EOF
    echo "✅ Created default async configuration"
fi

# Check for node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Verify backend connectivity
echo "🔍 Checking async backend connectivity..."
if curl -s "http://localhost:8001/health" > /dev/null 2>&1; then
    echo "✅ Async backend is running and accessible"
else
    echo "⚠️  Async backend not detected at http://localhost:8001"
    echo "📝 Make sure to start the async backend first:"
    echo "   ./start_backend_async.sh"
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
echo "📊 Configuration: ASYNC Backend (High Performance)"
echo "🔗 Backend API: http://localhost:8001"
echo "📖 API Docs: http://localhost:8001/docs"
echo "💚 Health Check: http://localhost:8001/health"
echo ""
echo "🌐 Frontend will be available at:"
echo "   📱 Next.js: http://localhost:3000"
echo "   ⚛️  React (CRA): http://localhost:3000"
echo "   ⚡ Vite: http://localhost:5173"
echo ""
echo "🛠️  Performance Features Enabled:"
echo "   ⚡ Redis caching for faster responses"
echo "   🔄 Async I/O for better concurrency"
echo "   📊 Performance monitoring"
echo "   🚀 Batch operations support"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the frontend development server
npm run $DEV_SCRIPT