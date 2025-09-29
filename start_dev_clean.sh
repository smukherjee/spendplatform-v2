#!/bin/bash

# Script to start both backend and frontend servers for development
# Uses nohup to ensure persistent execution

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[OK] $1${NC}"
}

print_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

print_warn() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Function to check if port is available
is_port_available() {
    ! lsof -i:$1 >/dev/null 2>&1
}

# Function to start backend with nohup
start_backend() {
    print_info "Starting Backend Server (Port 8001)..."
    
    if ! is_port_available 8001; then
        print_warn "Port 8001 is already in use. Stopping existing server..."
        pkill -f "uvicorn.*main:app" || true
        sleep 3
    fi
    
    # Start backend with nohup for persistent execution
    print_info "Launching backend with nohup..."
    nohup ./start_backend.sh > backend_dev.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend_dev.pid
    
    # Wait for backend to start
    print_info "Waiting for backend to start..."
    for i in {1..20}; do
        if curl -s http://localhost:8001/health >/dev/null 2>&1; then
            print_status "Backend server is running on http://localhost:8001 (PID: $BACKEND_PID)"
            print_info "Backend logs: tail -f backend_dev.log"
            return 0
        fi
        
        if [ $i -eq 20 ]; then
            print_error "Backend failed to start within 20 seconds"
            print_error "Check logs: tail -f backend_dev.log"
            return 1
        fi
        
        echo -n "."
        sleep 1
    done
}

# Function to start frontend with nohup
start_frontend() {
    print_info "Starting Frontend Server (Port 3000)..."
    
    if ! is_port_available 3000; then
        print_warn "Port 3000 is already in use. Stopping existing server..."
        pkill -f "react-scripts" || true
        sleep 3
    fi
    
    # Start frontend with nohup for persistent execution
    print_info "Launching frontend with nohup..."
    nohup ./start_frontend.sh > frontend_dev.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > frontend_dev.pid
    
    print_status "Frontend server is starting on http://localhost:3000 (PID: $FRONTEND_PID)"
    print_info "Frontend logs: tail -f frontend_dev.log"
}

# Function to cleanup on exit
cleanup() {
    print_info "Shutting down servers..."
    
    # Kill processes using PID files
    if [ -f backend_dev.pid ]; then
        BACKEND_PID=$(cat backend_dev.pid)
        kill $BACKEND_PID 2>/dev/null || true
        rm -f backend_dev.pid
    fi
    
    if [ -f frontend_dev.pid ]; then
        FRONTEND_PID=$(cat frontend_dev.pid)
        kill $FRONTEND_PID 2>/dev/null || true
        rm -f frontend_dev.pid
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -f "react-scripts" 2>/dev/null || true
    
    print_status "Development servers stopped"
}

# Function to test auth endpoint
test_auth() {
    print_info "Testing authentication endpoint..."
    sleep 2  # Give backend a moment to fully start
    
    AUTH_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=superadmin&password=superadmin123" || echo "FAILED")
    
    if [[ "$AUTH_RESPONSE" == *"access_token"* ]]; then
        print_status "Authentication endpoint working correctly"
        echo "Response contains access_token"
    else
        print_error "Authentication test failed"
        echo "Response: $AUTH_RESPONSE"
    fi
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Main execution
main() {
    echo ""
    echo "SpendPlatform v2 - Development Environment"
    echo "=========================================="
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "start_backend.sh" ] || [ ! -f "start_frontend.sh" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Start backend with nohup
    if ! start_backend; then
        print_error "Failed to start backend server"
        exit 1
    fi
    
    # Test authentication
    test_auth
    
    # Wait a moment
    sleep 2
    
    # Start frontend with nohup
    start_frontend
    
    # Display information
    echo ""
    echo "Server URLs:"
    echo "   Backend: http://localhost:8001"
    echo "   API Docs: http://localhost:8001/docs"
    echo "   Health Check: http://localhost:8001/health"
    echo "   Frontend: http://localhost:3000"
    echo ""
    echo "Test Credentials:"
    echo "   Username: superadmin"
    echo "   Password: superadmin123"
    echo ""
    echo "Log Files:"
    echo "   Backend: tail -f backend_dev.log"
    echo "   Frontend: tail -f frontend_dev.log"
    echo ""
    echo "Usage:"
    echo "   Press Ctrl+C to stop all servers"
    echo "   Servers run with nohup for persistence"
    echo ""
    
    # Wait for user to stop
    print_info "Development servers are running with nohup. Press Ctrl+C to stop..."
    
    # Keep the script running and show status
    while true; do
        sleep 10
        if ! curl -s http://localhost:8001/health >/dev/null 2>&1; then
            print_error "Backend server appears to be down!"
            break
        fi
    done
}

# Run main function
main "$@"