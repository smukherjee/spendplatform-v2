#!/bin/bash

# Script to run Frontend server from project root directory
# This script navigates to the frontend directory and starts the development server

# Get the directory where this script is located (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
echo "📊 Using npm run $DEV_SCRIPT"
echo "📊 Frontend will be available at:"
echo "   🌐 Next.js: http://localhost:3000"
echo "   ⚛️  React (CRA): http://localhost:3000"
echo "   ⚡ Vite: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop the server"

# Start the frontend development server
npm run $DEV_SCRIPT