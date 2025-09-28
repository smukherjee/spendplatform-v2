#!/bin/bash

# Script to start both backend and frontend servers in separate terminal windows
# This provides a full-stack development environment with easy debug log viewing

echo "🚀 Starting SpendPlatform v2 - Full Stack Development"
echo "📺 Opening servers in separate terminal windows for easy debugging"
echo ""

# Get the directory where this script is located (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
        gnome-terminal --title="$title" --working-directory="$SCRIPT_DIR" -- bash -c "echo '🏷️  $title' && $command; exec bash"
    elif command -v xterm >/dev/null 2>&1; then
        # Linux with xterm
        xterm -title "$title" -e "cd '$SCRIPT_DIR' && echo '🏷️  $title' && $command && bash" &
    elif command -v konsole >/dev/null 2>&1; then
        # Linux with KDE Konsole
        konsole --workdir "$SCRIPT_DIR" --title "$title" -e bash -c "echo '🏷️  $title' && $command; exec bash" &
    else
        echo "❌ Could not detect a supported terminal application"
        echo "ℹ️  Please run the servers manually:"
        echo "   ./start_backend.sh"
        if [ "$FRONTEND_EXISTS" = true ]; then
            echo "   ./start_frontend.sh"
        fi
        exit 1
    fi
}

echo "🔧 Opening backend server in new terminal..."
open_new_terminal "SpendPlatform Backend (FastAPI)" "./start_backend.sh"

# Wait a moment for backend to start
sleep 3

echo "✅ Backend terminal opened"

# Start frontend if it exists
if [ "$FRONTEND_EXISTS" = true ]; then
    echo "🌐 Opening frontend server in new terminal..."
    open_new_terminal "SpendPlatform Frontend (React)" "./start_frontend.sh"
    
    echo "✅ Frontend terminal opened"
    echo ""
    echo "📊 Full Stack Development Environment Ready!"
    echo "   🔧 Backend API: http://localhost:8000"
    echo "   📖 API Docs: http://localhost:8000/docs"
    echo "   🌐 Frontend: http://localhost:3000"
    echo ""
    echo "💡 Tips:"
    echo "   • Backend logs are visible in the Backend terminal window"
    echo "   • Frontend logs are visible in the Frontend terminal window"
    echo "   • Use Ctrl+C in each terminal to stop individual servers"
    echo "   • Close terminal windows when done developing"
else
    echo "ℹ️  No frontend found - only backend terminal opened"
    echo ""
    echo "📊 Backend Development Environment Ready!"
    echo "   🔧 Backend API: http://localhost:8000"
    echo "   📖 API Docs: http://localhost:8000/docs"
    echo ""
    echo "� Tips:"
    echo "   • Backend logs are visible in the Backend terminal window"
    echo "   • Use Ctrl+C in the backend terminal to stop the server"
fi

echo ""
echo "🚀 Development servers are starting in separate terminals"
echo "📋 Quick Commands:"
echo "   curl http://localhost:8000/health  # Test backend"
echo "   open http://localhost:8000/docs    # Open API docs"
if [ "$FRONTEND_EXISTS" = true ]; then
    echo "   open http://localhost:3000         # Open frontend"
fi
echo ""
echo "✨ Happy coding! The servers are running in their own terminal windows."