#!/bin/bash#!/bin/bash#!/bin/bash



# Script to start both backend and frontend servers for development

# Uses nohup to ensure persistent execution

# Script to start both backend and frontend servers for development# Script to start both backend and frontend servers in separate terminal windows

set -e

# This script starts the async-only development environment# Start async backend server

# Colors for output

GREEN='\033[0;32m'echo "🚀 Starting Backend Server..."

BLUE='\033[0;34m'

YELLOW='\033[1;33m'set -eopen_new_terminal "Backend (Port 8001)" "./start_backend.sh"

RED='\033[0;31m'

NC='\033[0m' # No Color



# Function to print colored output# Colors for output# Wait a moment for backend to start

print_status() {

    echo -e "${GREEN}✅ $1${NC}"GREEN='\033[0;32m'sleep 2TED: Now echo "🔗 Server URLs:"

}

BLUE='\033[0;34m'echo echo "💡 Usage:"

print_info() {

    echo -e "${BLUE}ℹ️  $1${NC}"YELLOW='\033[1;33m'echo "   ./start_dev.sh        # Start full-stack development environment"🔥 Backend: http://localhost:8001"

}

RED='\033[0;31m'echo "   📊 API Docs: http://localhost:8001/docs"

print_warn() {

    echo -e "${YELLOW}⚠️  $1${NC}"NC='\033[0m' # No Colorecho "   💚 Health Check: http://localhost:8001/health"

}

echo "   🔐 Test Login: superadmin/superadmin123"nc/sync backend serveecho "🛠️  Development Tools:"

print_error() {

    echo -e "${RED}❌ $1${NC}"# Function to print colored outputecho "   📝 Backend Config: python backend/src/server_config.py"

}

print_status() {echo "   🔄 Switch Backend to Async: python backend/src/server_config.py async"

# Function to check if port is available

is_port_available() {    echo -e "${GREEN}✅ $1${NC}"echo "   🔄 Switch Backend to Sync: python backend/src/server_config.py sync"

    ! lsof -i:$1 >/dev/null 2>&1

}}echo "   🏥 Backend Health Check: python backend/src/server_config.py health"



# Function to start backend with nohupecho ""

start_backend() {

    print_info "Starting Backend Server (Port 8001)..."print_info() {echo "   🌐 Frontend Config: ./frontend_config.sh"

    

    if ! is_port_available 8001; then    echo -e "${BLUE}ℹ️  $1${NC}"echo "   🔄 Switch Frontend to Async: ./frontend_config.sh async"

        print_warn "Port 8001 is already in use. Stopping existing server..."

        pkill -f "uvicorn.*main:app" || true}echo "   🔄 Switch Frontend to Sync: ./frontend_config.sh sync"

        sleep 3

    fiecho "   🏥 Frontend Health Check: ./frontend_config.sh health"ection

    

    # Start backend with nohup for persistent executionprint_warn() {# This provides a full-stack development environment with easy debug log viewing

    print_info "Launching backend with nohup..."

    nohup ./start_backend.sh > backend_dev.log 2>&1 &    echo -e "${YELLOW}⚠️  $1${NC}"

    BACKEND_PID=$!

    echo $BACKEND_PID > backend_dev.pid}echo "🚀 Starting SpendPlatform v2 - Full Stack Development"

    

    # Wait for backend to startecho "📺 Opening servers in separate terminal windows for easy debugging"

    print_info "Waiting for backend to start..."

    for i in {1..20}; doprint_error() {echo ""

        if curl -s http://localhost:8001/health >/dev/null 2>&1; then

            print_status "Backend server is running on http://localhost:8001 (PID: $BACKEND_PID)"    echo -e "${RED}❌ $1${NC}"

            print_info "Backend logs: tail -f backend_dev.log"

            return 0}# Get the directory where this script is located (project root)

        fi

        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

        if [ $i -eq 20 ]; then

            print_error "Backend failed to start within 20 seconds"# Function to check if a command exists

            print_error "Check logs: tail -f backend_dev.log"

            return 1command_exists() {echo "🔧 Starting High-Performance Async Server"

        fi

            command -v "$1" >/dev/null 2>&1echo "⚡ Backend: Port 8001 with Redis caching, async I/O, performance monitoring"

        echo -n "."

        sleep 1}echo "⚛️  Frontend: Configured for async backend connection"

    done

}echo ""



# Function to start frontend with nohup# Function to check if port is available

start_frontend() {

    print_info "Starting Frontend Server (Port 3000)..."is_port_available() {# Check if frontend exists

    

    if ! is_port_available 3000; then    ! lsof -i:$1 >/dev/null 2>&1FRONTEND_EXISTS=false

        print_warn "Port 3000 is already in use. Stopping existing server..."

        pkill -f "react-scripts" || true}if [ -d "$SCRIPT_DIR/frontend" ]; then

        sleep 3

    fi    FRONTEND_EXISTS=true

    

    # Start frontend with nohup for persistent execution# Function to start backendfi

    print_info "Launching frontend with nohup..."

    nohup ./start_frontend.sh > frontend_dev.log 2>&1 &start_backend() {

    FRONTEND_PID=$!

    echo $FRONTEND_PID > frontend_dev.pid    print_info "Starting Backend Server (Port 8001)..."# Function to detect terminal application and open new windows

    

    print_status "Frontend server is starting on http://localhost:3000 (PID: $FRONTEND_PID)"    open_new_terminal() {

    print_info "Frontend logs: tail -f frontend_dev.log"

}    if ! is_port_available 8001; then    local title="$1"



# Function to cleanup on exit        print_warn "Port 8001 is already in use. Attempting to stop existing server..."    local command="$2"

cleanup() {

    print_info "Shutting down servers..."        pkill -f "uvicorn.*main:app" || true    

    

    # Kill processes using PID files        sleep 2    # Try different terminal applications based on what's available

    if [ -f backend_dev.pid ]; then

        BACKEND_PID=$(cat backend_dev.pid)    fi    if command -v osascript >/dev/null 2>&1 && [[ "$OSTYPE" == "darwin"* ]]; then

        kill $BACKEND_PID 2>/dev/null || true

        rm -f backend_dev.pid            # macOS - try Terminal.app first, then iTerm2

    fi

        # Start backend in background        if pgrep -f "Terminal" > /dev/null || [[ "$TERM_PROGRAM" == "Apple_Terminal" ]]; then

    if [ -f frontend_dev.pid ]; then

        FRONTEND_PID=$(cat frontend_dev.pid)    ./start_backend.sh &            # Use Terminal.app

        kill $FRONTEND_PID 2>/dev/null || true

        rm -f frontend_dev.pid    BACKEND_PID=$!            osascript <<EOF

    fi

        tell application "Terminal"

    # Kill any remaining processes

    pkill -f "uvicorn.*main:app" 2>/dev/null || true    # Wait for backend to start    activate

    pkill -f "react-scripts" 2>/dev/null || true

        print_info "Waiting for backend to start..."    do script "cd '$SCRIPT_DIR' && echo '🏷️  $title' && $command"

    print_status "Development servers stopped"

}    for i in {1..15}; doend tell



# Function to test auth endpoint        if curl -s http://localhost:8001/health >/dev/null 2>&1; thenEOF

test_auth() {

    print_info "Testing authentication endpoint..."            print_status "Backend server is running on http://localhost:8001"        elif pgrep -f "iTerm" > /dev/null || [[ "$TERM_PROGRAM" == "iTerm.app" ]]; then

    sleep 2  # Give backend a moment to fully start

                break            # Use iTerm2

    AUTH_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/auth/token" \

        -H "Content-Type: application/x-www-form-urlencoded" \        fi            osascript <<EOF

        -d "username=superadmin&password=superadmin123" || echo "FAILED")

            tell application "iTerm"

    if [[ "$AUTH_RESPONSE" == *"access_token"* ]]; then

        print_status "Authentication endpoint working correctly"        if [ $i -eq 15 ]; then    activate

        echo "Response: $AUTH_RESPONSE" | head -c 100 && echo "..."

    else            print_error "Backend failed to start within 15 seconds"    create window with default profile

        print_error "Authentication test failed"

        echo "Response: $AUTH_RESPONSE"            return 1    tell current session of current window

    fi

}        fi        write text "cd '$SCRIPT_DIR' && echo '🏷️  $title' && $command"



# Set up signal handlers            end tell

trap cleanup EXIT INT TERM

        sleep 1end tell

# Main execution

main() {    doneEOF

    echo ""

    echo "🚀 SpendPlatform v2 - Development Environment"}        else

    echo "============================================="

    echo ""            # Fallback to Terminal.app

    

    # Check if we're in the right directory# Function to start frontend            osascript <<EOF

    if [ ! -f "start_backend.sh" ] || [ ! -f "start_frontend.sh" ]; then

        print_error "Please run this script from the project root directory"start_frontend() {tell application "Terminal"

        exit 1

    fi    print_info "Starting Frontend Server (Port 3000)..."    activate

    

    # Start backend with nohup        do script "cd '$SCRIPT_DIR' && echo '🏷️  $title' && $command"

    if ! start_backend; then

        print_error "Failed to start backend server"    if ! is_port_available 3000; thenend tell

        exit 1

    fi        print_warn "Port 3000 is already in use. Attempting to stop existing server..."EOF

    

    # Test authentication        pkill -f "react-scripts" || true        fi

    test_auth

            sleep 2    elif command -v gnome-terminal >/dev/null 2>&1; then

    # Wait a moment

    sleep 2    fi        # Linux with GNOME Terminal

    

    # Start frontend with nohup            gnome-terminal --title="$title" --working-directory="$SCRIPT_DIR" -- bash -c "echo '🏷️  $title' && $command; exec bash"

    start_frontend

        # Start frontend in background    elif command -v xterm >/dev/null 2>&1; then

    # Display information

    echo ""    ./start_frontend.sh &        # Linux with xterm

    echo "🔗 Server URLs:"

    echo "   🔥 Backend: http://localhost:8001"    FRONTEND_PID=$!        xterm -title "$title" -e "cd '$SCRIPT_DIR' && echo '🏷️  $title' && $command && bash" &

    echo "   📊 API Docs: http://localhost:8001/docs"

    echo "   💚 Health Check: http://localhost:8001/health"        elif command -v konsole >/dev/null 2>&1; then

    echo "   🌐 Frontend: http://localhost:3000"

    echo ""    print_status "Frontend server is starting on http://localhost:3000"        # Linux with KDE Konsole

    echo "🔐 Test Credentials:"

    echo "   Username: superadmin"}        konsole --workdir "$SCRIPT_DIR" --title "$title" -e bash -c "echo '🏷️  $title' && $command; exec bash" &

    echo "   Password: superadmin123"

    echo ""    else

    echo "📋 Log Files:"

    echo "   Backend: tail -f backend_dev.log"# Function to cleanup on exit        echo "❌ Could not detect a supported terminal application"

    echo "   Frontend: tail -f frontend_dev.log"

    echo ""cleanup() {        echo "ℹ️  Please run the servers manually:"

    echo "💡 Usage:"

    echo "   Press Ctrl+C to stop all servers"    print_info "Shutting down servers..."        echo "   ./start_backend.sh"

    echo "   Servers run with nohup for persistence"

    echo ""            if [ "$FRONTEND_EXISTS" = true ]; then

    

    # Wait for user to stop    if [ ! -z "$BACKEND_PID" ]; then            echo "   ./start_frontend.sh"

    print_info "Development servers are running with nohup. Press Ctrl+C to stop..."

            kill $BACKEND_PID 2>/dev/null || true        fi

    # Keep the script running and show status

    while true; do    fi        exit 1

        sleep 10

        if ! curl -s http://localhost:8001/health >/dev/null 2>&1; then        fi

            print_error "Backend server appears to be down!"

            break    if [ ! -z "$FRONTEND_PID" ]; then}

        fi

    done        kill $FRONTEND_PID 2>/dev/null || true

}

    fi# Start async backend server

# Run main function

main "$@"    echo "🚀 Starting Backend Server..."

    # Kill any remaining processesopen_new_terminal "� Backend (Port 8001)" "./start_backend.sh"

    pkill -f "uvicorn.*main:app" 2>/dev/null || true

    pkill -f "react-scripts" 2>/dev/null || true# Wait a moment for backend to start

    sleep 2

    print_status "Development servers stopped"

}# Start frontend server if it exists

if [ "$FRONTEND_EXISTS" = true ]; then

# Set up signal handlers    echo "🚀 Starting Frontend Server..."

trap cleanup EXIT INT TERM    open_new_terminal "Frontend (Port 3000)" "./start_frontend.sh"

    

# Main executionelse

main() {    echo "⚠️  Frontend directory not found at $SCRIPT_DIR/frontend"

    echo ""    echo "📝 Frontend server will need to be started manually once created"

    echo "🚀 SpendPlatform v2 - Development Environment"fi

    echo "============================================="

    echo ""echo ""

    echo "✅ Development environment started!"

    # Check if we're in the right directoryecho ""

    if [ ! -f "start_backend.sh" ] || [ ! -f "start_frontend.sh" ]; thenecho "🔗 Server URLs:"

        print_error "Please run this script from the project root directory"if [ "$BACKEND_TYPE" = "async" ]; then

        exit 1    echo "   � Backend (ASYNC): http://localhost:8001"

    fi    echo "   � API Docs: http://localhost:8001/docs"

        echo "   💚 Health Check: http://localhost:8001/health"

    # Start backend    echo "   � Test Login: superadmin/superadmin123"

    start_backendelse

        echo "   🐌 Backend (SYNC): http://localhost:8000"

    # Wait a moment    echo "   📊 API Docs: http://localhost:8000/docs"

    sleep 2    echo "   💚 Health Check: http://localhost:8000/health"

        echo "   🔐 Test Login: user/user123 or superadmin/superadmin123"

    # Start frontendfi

    start_frontend

    if [ "$FRONTEND_EXISTS" = true ]; then

    # Display information    echo "   ⚛️  Frontend: http://localhost:3000 (or check terminal for actual port)"

    echo ""fi

    echo "🔗 Server URLs:"

    echo "   🔥 Backend: http://localhost:8001"echo ""

    echo "   📊 API Docs: http://localhost:8001/docs"echo "�️  Development Tools:"

    echo "   💚 Health Check: http://localhost:8001/health"echo "   � Backend Config: python backend/src/server_config.py"

    echo "   🌐 Frontend: http://localhost:3000"echo "   � Switch to Async: python backend/src/server_config.py async"

    echo ""echo "   🔄 Switch to Sync: python backend/src/server_config.py sync"

    echo "🔐 Test Credentials:"echo "   🏥 Health Check: python backend/src/server_config.py health"

    echo "   Username: superadmin"echo ""

    echo "   Password: superadmin123"echo "� Usage:"

    echo ""echo "   ./start_dev.sh        # Start with async backend (default)"

    echo "💡 Usage:"echo "   ./start_dev.sh async  # Start with async backend"

    echo "   Press Ctrl+C to stop all servers"echo "   ./start_dev.sh sync   # Start with sync backend"

    echo ""echo ""

    echo "🚫 To stop all servers: pkill -f uvicorn && pkill -f npm"

    # Wait for user to stopecho "📺 Each server runs in its own terminal window for easy debugging"
    print_info "Development servers are running. Press Ctrl+C to stop..."
    
    # Keep the script running
    wait
}

# Run main function
main "$@"