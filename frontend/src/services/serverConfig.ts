// Frontend-Backend Server Connection Configuration Manager
// This utility helps switch between async and sync backend servers

export interface ServerConfig {
  baseURL: string;
  serverType: 'ASYNC' | 'SYNC';
  timeout: number;
  apiPrefix: string;
  testCredentials: {
    username: string;
    password: string;
  };
  features: {
    redis: boolean;
    caching: boolean;
    performanceHeaders: boolean;
  };
}

// ASYNC Server Configuration (Default - High Performance)
export const ASYNC_CONFIG: ServerConfig = {
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001',
  serverType: 'ASYNC',
  timeout: parseInt(process.env.REACT_APP_API_TIMEOUT || '10000'),
  apiPrefix: '/api/v1',
  testCredentials: {
    username: process.env.REACT_APP_DEFAULT_TEST_USER || 'superadmin',
    password: process.env.REACT_APP_DEFAULT_TEST_PASSWORD || 'superadmin123'
  },
  features: {
    redis: true,
    caching: true,
    performanceHeaders: true
  }
};

// SYNC Server Configuration (Backup - Traditional)
export const SYNC_CONFIG: ServerConfig = {
  baseURL: 'http://localhost:8000',
  serverType: 'SYNC',
  timeout: 5000,
  apiPrefix: '',
  testCredentials: {
    username: 'user',
    password: 'user123'
  },
  features: {
    redis: false,
    caching: false,
    performanceHeaders: false
  }
};

// Get current server configuration based on environment
export const getCurrentConfig = (): ServerConfig => {
  const serverType = process.env.REACT_APP_SERVER_TYPE || 'ASYNC';
  
  if (serverType === 'SYNC') {
    return SYNC_CONFIG;
  }
  
  return ASYNC_CONFIG;
};

// Get API endpoint with proper prefix
export const getApiEndpoint = (endpoint: string): string => {
  const config = getCurrentConfig();
  
  // Remove leading slash if present
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  
  // Add prefix for async server, no prefix for sync
  if (config.serverType === 'ASYNC') {
    return `${config.apiPrefix}/${cleanEndpoint}`;
  }
  
  return `/${cleanEndpoint}`;
};

// Server switching utilities
export const switchToAsyncServer = () => {
  console.log('🔄 Switching to ASYNC server (port 8001)...');
  console.log('⚡ Features: Redis caching, performance headers, enhanced async operations');
  console.log('🔐 Test credentials: superadmin/superadmin123');
  
  // In a real implementation, this would update environment variables
  // For now, it logs instructions
  console.log('📝 To switch permanently:');
  console.log('   1. Copy .env.async to .env');
  console.log('   2. Restart the React development server');
  console.log('   3. Update imports to use api-async.ts instead of api.ts if needed');
};

export const switchToSyncServer = () => {
  console.log('🔄 Switching to SYNC server (port 8000)...');
  console.log('🐌 Features: Traditional sync operations, no caching');
  console.log('🔐 Test credentials: user/user123');
  
  console.log('📝 To switch permanently:');
  console.log('   1. Copy .env.sync to .env');
  console.log('   2. Restart the React development server');
  console.log('   3. Update imports to use api-sync-backup.ts instead of api.ts if needed');
};

// Health check for both servers
export const checkBothServers = async () => {
  const results = {
    async: false,
    sync: false,
    asyncError: null as any,
    syncError: null as any
  };

  // Check async server
  try {
    const asyncResponse = await fetch('http://localhost:8001/health');
    results.async = asyncResponse.ok;
  } catch (error) {
    results.asyncError = error;
  }

  // Check sync server
  try {
    const syncResponse = await fetch('http://localhost:8000/health');
    results.sync = syncResponse.ok;
  } catch (error) {
    results.syncError = error;
  }

  return results;
};

// Display current configuration
export const displayCurrentConfig = () => {
  const config = getCurrentConfig();
  
  console.log('🔧 Current Frontend Configuration:');
  console.log(`   Server Type: ${config.serverType}`);
  console.log(`   Base URL: ${config.baseURL}`);
  console.log(`   API Prefix: ${config.apiPrefix || 'None'}`);
  console.log(`   Timeout: ${config.timeout}ms`);
  console.log(`   Redis Caching: ${config.features.redis ? 'Enabled' : 'Disabled'}`);
  console.log(`   Performance Headers: ${config.features.performanceHeaders ? 'Enabled' : 'Disabled'}`);
  console.log(`   Test User: ${config.testCredentials.username}`);
  
  return config;
};

export default {
  ASYNC_CONFIG,
  SYNC_CONFIG,
  getCurrentConfig,
  getApiEndpoint,
  switchToAsyncServer,
  switchToSyncServer,
  checkBothServers,
  displayCurrentConfig
};