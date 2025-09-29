#!/usr/bin/env python3
"""
Backend Server Configuration Management Utility
Helps switch between async and sync backend servers
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

# Server configurations
ASYNC_CONFIG = {
    "name": "ASYNC",
    "port": 8001,
    "host": "0.0.0.0",
    "main_file": "main_async:app",
    "features": ["Redis Caching", "Async I/O", "Performance Monitoring", "Enhanced Logging"],
    "endpoints": 43,
    "test_credentials": "superadmin/superadmin123",
    "env_file": ".env.async",
    "database": "spendplatform_async.db"
}

SYNC_CONFIG = {
    "name": "SYNC",
    "port": 8000,
    "host": "0.0.0.0",
    "main_file": "main:app",
    "features": ["Traditional Sync I/O", "Standard Endpoints"],
    "endpoints": 20,
    "test_credentials": "user/user123 or superadmin/superadmin123",
    "env_file": ".env.sync",
    "database": "spendplatform_sync.db"
}

def get_project_root() -> Path:
    """Get the project root directory"""
    current = Path(__file__).parent
    while current.parent != current:
        if (current / "start_backend.sh").exists():
            return current
        current = current.parent
    return Path.cwd()

def check_server_health(port: int) -> Tuple[bool, Optional[Dict]]:
    """Check if server is running and healthy"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except Exception as e:
        return False, {"error": str(e)}

def get_current_server_type() -> str:
    """Determine current server type from environment"""
    env_file = get_project_root() / "backend" / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if "SERVER_TYPE=ASYNC" in content:
                return "ASYNC"
            elif "SERVER_TYPE=SYNC" in content:
                return "SYNC"
    return "UNKNOWN"

def switch_to_async():
    """Switch backend to async server configuration"""
    project_root = get_project_root()
    backend_dir = project_root / "backend"
    
    print("🔄 Switching to ASYNC backend server...")
    
    # Copy async environment
    env_async = backend_dir / ".env.async"
    env_target = backend_dir / ".env"
    
    if env_async.exists():
        subprocess.run(["cp", str(env_async), str(env_target)])
        print("✅ Environment configuration updated")
    else:
        print("❌ .env.async file not found")
        return False
    
    print("⚡ ASYNC server configuration active")
    print(f"🌐 Server will run on: http://localhost:{ASYNC_CONFIG['port']}")
    print(f"🔐 Test credentials: {ASYNC_CONFIG['test_credentials']}")
    print(f"🚀 Features: {', '.join(ASYNC_CONFIG['features'])}")
    print("")
    print("To start the server, run:")
    print("  ./start_backend_async.sh")
    print("  # OR")
    print("  ./start_backend.sh  # (now defaults to async)")
    
    return True

def switch_to_sync():
    """Switch backend to sync server configuration"""
    project_root = get_project_root()
    backend_dir = project_root / "backend"
    
    print("🔄 Switching to SYNC backend server...")
    
    # Copy sync environment
    env_sync = backend_dir / ".env.sync"
    env_target = backend_dir / ".env"
    
    if env_sync.exists():
        subprocess.run(["cp", str(env_sync), str(env_target)])
        print("✅ Environment configuration updated")
    else:
        print("❌ .env.sync file not found")
        return False
    
    print("🐌 SYNC server configuration active")
    print(f"🌐 Server will run on: http://localhost:{SYNC_CONFIG['port']}")
    print(f"🔐 Test credentials: {SYNC_CONFIG['test_credentials']}")
    print(f"🚀 Features: {', '.join(SYNC_CONFIG['features'])}")
    print("")
    print("To start the server, run:")
    print("  ./start_backend_sync.sh")
    print("  # OR")
    print("  BACKEND_SERVER_TYPE=sync ./start_backend.sh")
    
    return True

def display_current_config():
    """Display current backend configuration"""
    current_type = get_current_server_type()
    config = ASYNC_CONFIG if current_type == "ASYNC" else SYNC_CONFIG
    
    print("🔧 Current Backend Configuration:")
    print(f"   Server Type: {config['name']}")
    print(f"   Port: {config['port']}")
    print(f"   Host: {config['host']}")
    print(f"   Main File: {config['main_file']}")
    print(f"   Database: {config['database']}")
    print(f"   Features: {', '.join(config['features'])}")
    print(f"   Endpoints: {config['endpoints']}+")
    print(f"   Test Credentials: {config['test_credentials']}")
    print(f"   Environment File: {config['env_file']}")
    print("")
    
    return config

def check_both_servers():
    """Check the health of both servers"""
    print("🔍 Checking server health...")
    
    # Check async server
    async_healthy, async_data = check_server_health(ASYNC_CONFIG['port'])
    print(f"⚡ ASYNC Server (port {ASYNC_CONFIG['port']}): {'✅ HEALTHY' if async_healthy else '❌ NOT RUNNING'}")
    if async_healthy and async_data:
        print(f"   Services: {async_data.get('services', 'Unknown')}")
        print(f"   Version: {async_data.get('version', 'Unknown')}")
    
    # Check sync server
    sync_healthy, sync_data = check_server_health(SYNC_CONFIG['port'])
    print(f"🐌 SYNC Server (port {SYNC_CONFIG['port']}): {'✅ HEALTHY' if sync_healthy else '❌ NOT RUNNING'}")
    if sync_healthy and sync_data:
        print(f"   Status: {sync_data.get('status', 'Unknown')}")
    
    print("")
    return {
        "async": {"healthy": async_healthy, "data": async_data},
        "sync": {"healthy": sync_healthy, "data": sync_data}
    }

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("🔧 Backend Server Configuration Manager")
        print("")
        print("Usage:")
        print("  python server_config.py status     # Show current configuration")
        print("  python server_config.py async      # Switch to async server")
        print("  python server_config.py sync       # Switch to sync server")
        print("  python server_config.py health     # Check both servers")
        print("")
        display_current_config()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        display_current_config()
    elif command == "async":
        switch_to_async()
    elif command == "sync":
        switch_to_sync()
    elif command == "health":
        check_both_servers()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: status, async, sync, health")

if __name__ == "__main__":
    main()