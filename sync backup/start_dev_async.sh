#!/bin/bash

# Script to start both backend and frontend servers in separate terminal windows
# UPDATED: Now supports async/sync backend server selection
# This provides a full-stack development environment with easy debug log viewing

echo "🚀 Starting SpendPlatform v2 - Full Stack Development"
echo "📺 Opening servers in separate terminal windows for easy debugging"
echo ""

# Get the directory where this script is located (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check server type preference
BACKEND_TYPE="${BACKEND_SERVER_TYPE:-async}"
if [ "$1" = "sync" ]; then
    BACKEND_TYPE="sync"
elif [ "$1" = "async" ]; then
    BACKEND_TYPE="async"
fi

echo "🔧 Backend Server Type: $BACKEND_TYPE"
if [ "$BACKEND_TYPE" = "async" ]; then
    echo "⚡ Using high-performance async server (port 8001)"
    echo "🔗 Features: Redis caching, async I/O, performance monitoring"
else
    echo "🐌 Using traditional sync server (port 8000)"
    echo "🔗 Features: Standard sync I/O, basic endpoints"
fi
echo ""

# Check if frontend exists
FRONTEND_EXISTS=false
if [ -d "$SCRIPT_DIR/frontend" ]; then
    FRONTEND_EXISTS=true
fi

# Function to detect terminal application and open new windows
open_new_terminal() {
    local title="$1"
    local command="$2"
    
    # Try different terminal applications based on what's available
    if command -v osascript >/dev/null 2>&1 && [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - try Terminal.app first, then iTerm2
        if pgrep -f "Terminal" > /dev/null || [[ "$TERM_PROGRAM" == "Apple_Terminal" ]]; then
            # Use Terminal.app
            osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$SCRIPT_DIR' && echo '🏷️  $title' && $command"
end tell
EOF
        elif pgrep -f "iTerm" > /dev/null || [[ "$TERM_PROGRAM" == "iTerm.app" ]]; then
            # Use iTerm2
            osascript <<EOF
tell application "iTerm"
    activate
    create window with default profile
    tell current session of current window
        write text "cd '$SCRIPT_DIR' && echo '🏷️  $title' && $command"
    end tell
end tell
EOF
        else
            # Fallback to Terminal.app
            osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$SCRIPT_DIR' && echo '🏷️  $title' && $command"
end tell
EOF
        fi
    elif command -v gnome-terminal >/dev/null 2>&1; then
        # Linux with GNOME Terminal
        gnome-terminal --title="$title" -- bash -c "cd '$SCRIPT_DIR' && echo '🏷️  $title' && $command; exec bash"
    elif command -v konsole >/dev/null 2>&1; then
        # Linux with Konsole (KDE)
        konsole --title "$title" -e bash -c "cd '$SCRIPT_DIR' && echo '🏷️  $title' && $command; exec bash" &
    elif command -v xterm >/dev/null 2>&1; then
        # Fallback to xterm
        xterm -title "$title" -e bash -c "cd '$SCRIPT_DIR' && echo '🏷️  $title' && $command; exec bash" &
    else
        # No terminal multiplexer found, run in current terminal with background processes
        echo "⚠️  No supported terminal application found. Running servers in background..."
        echo "🏷️  $title"
        cd "$SCRIPT_DIR"
        eval "$command" &
        cd - > /dev/null
    fi
}

# Kill any existing servers
echo "🔄 Stopping any existing servers..."
pkill -f uvicorn 2>/dev/null || true
pkill -f "python.*main:app" 2>/dev/null || true
pkill -f "python.*main_async:app" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

# Wait for processes to stop
sleep 3

# Start backend server based on type
if [ "$BACKEND_TYPE" = "async" ]; then
    echo "🚀 Starting ASYNC Backend Server..."
    open_new_terminal "🔥 ASYNC Backend (Port 8001)" "./start_backend_async.sh"
else
    echo "🚀 Starting SYNC Backend Server..."
    open_new_terminal "🐌 SYNC Backend (Port 8000)" "./start_backend_sync.sh"
fi

# Wait a moment for backend to start
sleep 2

# Start frontend server if it exists
if [ "$FRONTEND_EXISTS" = true ]; then
    echo "🚀 Starting Frontend Server..."
    if [ "$BACKEND_TYPE" = "async" ]; then
        # Ensure frontend is configured for async server
        open_new_terminal "⚛️  Frontend (Async Config)" "cd frontend && cp .env.async .env 2>/dev/null || true && ./start_frontend.sh"
    else
        # Ensure frontend is configured for sync server
        open_new_terminal "⚛️  Frontend (Sync Config)" "cd frontend && cp .env.sync .env 2>/dev/null || true && ./start_frontend.sh"
    fi
else
    echo "⚠️  Frontend directory not found at $SCRIPT_DIR/frontend"
    echo "📝 Frontend server will need to be started manually once created"
fi

echo ""
echo "✅ Development environment started!"
echo ""
echo "🔗 Server URLs:"
if [ "$BACKEND_TYPE" = "async" ]; then
    echo "   🔥 Backend (ASYNC): http://localhost:8001"
    echo "   📊 API Docs: http://localhost:8001/docs"
    echo "   💚 Health Check: http://localhost:8001/health"
    echo "   🔐 Test Login: superadmin/superadmin123"
else
    echo "   🐌 Backend (SYNC): http://localhost:8000"
    echo "   📊 API Docs: http://localhost:8000/docs"
    echo "   💚 Health Check: http://localhost:8000/health"
    echo "   🔐 Test Login: user/user123 or superadmin/superadmin123"
fi

if [ "$FRONTEND_EXISTS" = true ]; then
    echo "   ⚛️  Frontend: http://localhost:3000 (or check terminal for actual port)"
fi

echo ""
echo "🛠️  Development Tools:"
echo "   📝 Backend Config: python backend/src/server_config.py"
echo "   🔄 Switch to Async: python backend/src/server_config.py async"
echo "   🔄 Switch to Sync: python backend/src/server_config.py sync"
echo "   🏥 Health Check: python backend/src/server_config.py health"
echo ""
echo "💡 Usage:"
echo "   ./start_dev.sh        # Start with async backend (default)"
echo "   ./start_dev.sh async  # Start with async backend"
echo "   ./start_dev.sh sync   # Start with sync backend"
echo ""
echo "🚫 To stop all servers: pkill -f uvicorn && pkill -f npm"
echo "📺 Each server runs in its own terminal window for easy debugging"