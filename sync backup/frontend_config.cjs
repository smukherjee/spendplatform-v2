#!/usr/bin/env node

/**
 * Frontend Configuration Utility
 * Manages frontend environment switching between async and sync backend connections
 * Usage: node frontend_config.js [command] [args]
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const FRONTEND_DIR = path.join(__dirname, 'frontend');
const ENV_FILE = path.join(FRONTEND_DIR, '.env');
const ENV_ASYNC_FILE = path.join(FRONTEND_DIR, '.env.async');
const ENV_SYNC_FILE = path.join(FRONTEND_DIR, '.env.sync');

// Colors for console output
const colors = {
    reset: '\x1b[0m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    white: '\x1b[37m'
};

function colorize(text, color) {
    return `${colors[color]}${text}${colors.reset}`;
}

function checkFrontendExists() {
    if (!fs.existsSync(FRONTEND_DIR)) {
        console.log(colorize('❌ Frontend directory not found', 'red'));
        console.log(colorize('📝 Please create the frontend directory first', 'yellow'));
        process.exit(1);
    }
}

function readEnvFile(filePath) {
    if (!fs.existsSync(filePath)) {
        return {};
    }
    
    const content = fs.readFileSync(filePath, 'utf8');
    const env = {};
    
    content.split('\n').forEach(line => {
        line = line.trim();
        if (line && !line.startsWith('#') && line.includes('=')) {
            const [key, ...valueParts] = line.split('=');
            env[key.trim()] = valueParts.join('=').trim();
        }
    });
    
    return env;
}

function getCurrentConfig() {
    const env = readEnvFile(ENV_FILE);
    const backendUrl = env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
    let backendType = env.REACT_APP_BACKEND_TYPE || 'sync';
    
    // Determine backend type from URL if not explicitly set
    if (backendUrl.includes(':8001')) {
        backendType = 'async';
    } else if (backendUrl.includes(':8000')) {
        backendType = 'sync';
    }
    
    return {
        backendUrl,
        backendType,
        isAsync: backendType === 'async',
        isSync: backendType === 'sync'
    };
}

function checkBackendHealth(url) {
    try {
        const response = execSync(`curl -s -o /dev/null -w "%{http_code}" "${url}/health"`, { 
            encoding: 'utf8',
            timeout: 5000
        });
        return response.trim() === '200';
    } catch (error) {
        return false;
    }
}

function switchToAsync() {
    checkFrontendExists();
    
    console.log(colorize('🔄 Switching frontend to ASYNC backend configuration...', 'cyan'));
    
    if (fs.existsSync(ENV_ASYNC_FILE)) {
        fs.copyFileSync(ENV_ASYNC_FILE, ENV_FILE);
        console.log(colorize('✅ Switched to async backend configuration', 'green'));
    } else {
        // Create default async configuration
        const asyncConfig = `# Frontend Configuration for ASYNC Backend
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
`;
        
        fs.writeFileSync(ENV_FILE, asyncConfig);
        fs.writeFileSync(ENV_ASYNC_FILE, asyncConfig);
        console.log(colorize('✅ Created and switched to async backend configuration', 'green'));
    }
    
    showCurrentStatus();
}

function switchToSync() {
    checkFrontendExists();
    
    console.log(colorize('🔄 Switching frontend to SYNC backend configuration...', 'cyan'));
    
    if (fs.existsSync(ENV_SYNC_FILE)) {
        fs.copyFileSync(ENV_SYNC_FILE, ENV_FILE);
        console.log(colorize('✅ Switched to sync backend configuration', 'green'));
    } else {
        // Create default sync configuration
        const syncConfig = `# Frontend Configuration for SYNC Backend
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
`;
        
        fs.writeFileSync(ENV_FILE, syncConfig);
        fs.writeFileSync(ENV_SYNC_FILE, syncConfig);
        console.log(colorize('✅ Created and switched to sync backend configuration', 'green'));
    }
    
    showCurrentStatus();
}

function showCurrentStatus() {
    checkFrontendExists();
    
    const config = getCurrentConfig();
    
    console.log(colorize('\n📊 Frontend Configuration Status', 'cyan'));
    console.log(colorize('================================', 'cyan'));
    console.log(`🔗 Backend URL: ${colorize(config.backendUrl, 'white')}`);
    console.log(`⚙️  Backend Type: ${colorize(config.backendType.toUpperCase(), config.isAsync ? 'green' : 'yellow')}`);
    
    if (config.isAsync) {
        console.log(`⚡ Mode: ${colorize('High-Performance Async', 'green')}`);
        console.log(`🔗 Features: ${colorize('Redis caching, async I/O, performance monitoring', 'green')}`);
    } else {
        console.log(`🐌 Mode: ${colorize('Traditional Sync', 'yellow')}`);
        console.log(`🔗 Features: ${colorize('Standard sync I/O, basic endpoints', 'yellow')}`);
    }
    
    // Check backend health
    console.log('\n🏥 Backend Health Check:');
    const asyncHealth = checkBackendHealth('http://localhost:8001');
    const syncHealth = checkBackendHealth('http://localhost:8000');
    
    console.log(`   ⚡ Async (8001): ${asyncHealth ? colorize('✅ Running', 'green') : colorize('❌ Not running', 'red')}`);
    console.log(`   🐌 Sync (8000):  ${syncHealth ? colorize('✅ Running', 'green') : colorize('❌ Not running', 'red')}`);
    
    if (config.isAsync && !asyncHealth) {
        console.log(colorize('\n⚠️  Warning: Frontend is configured for async backend but it\'s not running', 'yellow'));
        console.log(colorize('📝 Start async backend: ./start_backend_async.sh', 'yellow'));
    } else if (config.isSync && !syncHealth) {
        console.log(colorize('\n⚠️  Warning: Frontend is configured for sync backend but it\'s not running', 'yellow'));
        console.log(colorize('📝 Start sync backend: ./start_backend_sync.sh', 'yellow'));
    } else if ((config.isAsync && asyncHealth) || (config.isSync && syncHealth)) {
        console.log(colorize('\n✅ Frontend configuration matches running backend server', 'green'));
    }
}

function showEnvironmentFiles() {
    checkFrontendExists();
    
    console.log(colorize('\n📁 Environment Files Status', 'cyan'));
    console.log(colorize('============================', 'cyan'));
    
    const files = [
        { name: '.env', path: ENV_FILE, desc: 'Current active configuration' },
        { name: '.env.async', path: ENV_ASYNC_FILE, desc: 'Async backend configuration' },
        { name: '.env.sync', path: ENV_SYNC_FILE, desc: 'Sync backend configuration' }
    ];
    
    files.forEach(file => {
        const exists = fs.existsSync(file.path);
        const status = exists ? colorize('✅ Exists', 'green') : colorize('❌ Missing', 'red');
        console.log(`${file.name.padEnd(12)} ${status} - ${file.desc}`);
        
        if (exists && file.name === '.env') {
            const env = readEnvFile(file.path);
            const url = env.REACT_APP_API_BASE_URL || 'Not set';
            console.log(`${' '.repeat(15)}→ Backend URL: ${url}`);
        }
    });
}

function showHelp() {
    console.log(colorize('\n🛠️  Frontend Configuration Utility', 'cyan'));
    console.log(colorize('===================================', 'cyan'));
    console.log('\nManages frontend environment switching between async and sync backend connections\n');
    
    console.log(colorize('Commands:', 'white'));
    console.log('  status     Show current frontend configuration');
    console.log('  async      Switch to async backend (port 8001)');
    console.log('  sync       Switch to sync backend (port 8000)');
    console.log('  health     Check backend server health');
    console.log('  files      Show environment files status');
    console.log('  help       Show this help message');
    
    console.log(colorize('\nExamples:', 'white'));
    console.log('  node frontend_config.cjs status');
    console.log('  node frontend_config.cjs async');
    console.log('  node frontend_config.cjs sync');
    console.log('  node frontend_config.cjs health');
    
    console.log(colorize('\nFrontend Startup:', 'white'));
    console.log('  ./start_frontend.sh        # Use current configuration');
    console.log('  ./start_frontend.sh async  # Force async backend');
    console.log('  ./start_frontend.sh sync   # Force sync backend');
    console.log('  ./start_frontend_async.sh  # Dedicated async script');
    console.log('  ./start_frontend_sync.sh   # Dedicated sync script');
}

// Main execution
function main() {
    const command = process.argv[2] || 'status';
    
    switch (command.toLowerCase()) {
        case 'async':
            switchToAsync();
            break;
        case 'sync':
            switchToSync();
            break;
        case 'status':
        case 'show':
            showCurrentStatus();
            break;
        case 'health':
            console.log(colorize('🏥 Checking backend health...', 'cyan'));
            showCurrentStatus();
            break;
        case 'files':
        case 'env':
            showEnvironmentFiles();
            break;
        case 'help':
        case '--help':
        case '-h':
            showHelp();
            break;
        default:
            console.log(colorize(`❌ Unknown command: ${command}`, 'red'));
            console.log(colorize('Use "node frontend_config.js help" for available commands', 'yellow'));
            process.exit(1);
    }
}

// Handle errors gracefully
process.on('uncaughtException', (error) => {
    console.log(colorize(`❌ Error: ${error.message}`, 'red'));
    process.exit(1);
});

process.on('unhandledRejection', (error) => {
    console.log(colorize(`❌ Error: ${error.message}`, 'red'));
    process.exit(1);
});

if (require.main === module) {
    main();
}

module.exports = {
    switchToAsync,
    switchToSync,
    showCurrentStatus,
    getCurrentConfig,
    checkBackendHealth
};