// UPDATED: API service now connects to ASYNC backend server for enhanced performance
// Original sync server backup available in api-sync-backup.ts
// Async server configuration available in api-async.ts
import axios from 'axios';

// ASYNC server configuration - connects to port 8001 with Redis caching
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api/v1';
const API_ROOT_URL = API_BASE_URL.replace(/\/api\/v1\/?$/, '');

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 10000, // 10 second timeout for async operations
});

// Add JWT token to requests
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('access_token');
  
  // Log all outgoing requests for debugging
  console.log(`🚀 API Request (ASYNC): ${config.method?.toUpperCase()} ${config.url}`);
  console.log('⚡ Connected to async server on port 8001');
  console.log('📋 Request data:', config.data);
  
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log('🔐 Auth token added to async request');
    
    // Decode and log token info (for debugging)
    try {
      const tokenPayload = token.split('.')[1];
      const decodedPayload = JSON.parse(atob(tokenPayload));
      console.log('👤 Token user info (ASYNC):', {
        username: decodedPayload.sub,
        role: decodedPayload.role,
        client_id: decodedPayload.client_id,
        exp: new Date(decodedPayload.exp * 1000)
      });
    } catch (e) {
      console.warn('⚠️ Could not decode token for debugging');
    }
  } else {
    console.warn('🔐 No auth token found - async API calls may fail');
    if (process.env.NODE_ENV === 'development') {
      console.warn('🔧 Development mode: Consider implementing auto-login for testing');
    }
  }
  return config;
});

// Handle token refresh on 401 errors
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response (ASYNC): ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`);
    // Log cache headers if present
    if (response.headers['x-cache-status']) {
      console.log(`💾 Cache Status: ${response.headers['x-cache-status']}`);
    }
    if (response.headers['x-cache-ttl']) {
      console.log(`⏰ Cache TTL: ${response.headers['x-cache-ttl']}s`);
    }
    return response;
  },
  async (error) => {
    console.error(`❌ API Error (ASYNC): ${error.response?.status} ${error.config?.method?.toUpperCase()} ${error.config?.url}`);
    console.error('📄 Error response data:', error.response?.data);
    
    if (error.response?.status === 401) {
      console.warn('🚫 401 Unauthorized - attempting token refresh on async server...');
      // Try to refresh token or redirect to login
      const refreshToken = sessionStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
      const response = await api.post('/auth/refresh', {
            refresh_token: refreshToken
          });
          const newToken = (response.data as any).access_token;
          sessionStorage.setItem('access_token', newToken);
          // Retry the original request
          if (error.config.headers) {
            error.config.headers.Authorization = `Bearer ${newToken}`;
          }
          return api.request(error.config);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          sessionStorage.removeItem('access_token');
          sessionStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      } else {
        // No refresh token, redirect to login
        sessionStorage.removeItem('access_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth functions for ASYNC server (note the /api/v1 prefix)
export async function login(username: string, password: string) {
  try {
    console.log('🔄 Starting login process...');
    
    // FastAPI OAuth2PasswordRequestForm expects application/x-www-form-urlencoded
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    
    console.log('📡 Requesting token from /auth/token...');
    const response = await api.post('/auth/token', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    const data = response.data as { access_token: string; token_type: string };
    sessionStorage.setItem('access_token', data.access_token);
    sessionStorage.setItem('token_type', data.token_type || 'bearer');
    
    console.log('✅ Token received and stored');
    
    // Now call /auth/me to get complete user profile
    console.log('📡 Fetching user profile from /auth/me...');
    try {
      const userProfile = await fetchCurrentUser();
      console.log('✅ User profile fetched:', userProfile);
      
      // Create user data object with complete profile
      const userData = {
        id: userProfile.id,
        username: userProfile.username,
        email: userProfile.email,
        role: userProfile.roles ? userProfile.roles[0] : 'user',
        roles: userProfile.roles || [],
        client_id: userProfile.client_id,
        user_id: userProfile.id,
        personalisation: userProfile.personalisation
      };
      
      console.log('✅ Login successful with complete user profile:', userData);
      return { ...response.data, user: userData };
    } catch (profileError) {
      console.warn('⚠️ Could not fetch user profile, falling back to token payload:', profileError);
      
      // Fallback to JWT token decode if /auth/me fails
      try {
        const tokenPayload = data.access_token.split('.')[1];
        const decodedPayload = JSON.parse(atob(tokenPayload));
        const userData = {
          username: decodedPayload.sub,
          role: decodedPayload.roles ? decodedPayload.roles[0] : 'user',
          roles: decodedPayload.roles || [],
          client_id: decodedPayload.client_id,
          user_id: decodedPayload.user_id
        };
        
        console.log('⚠️ Using fallback token payload data:', userData);
        return { ...response.data, user: userData };
      } catch (decodeError) {
        console.warn('❌ Could not decode token payload:', decodeError);
        return response.data;
      }
    }
  } catch (error) {
    console.error('❌ Login failed:', error);
    throw error;
  }
}

// Fetch current user profile from server
export async function fetchCurrentUser() {
  try {
    const response = await api.get('/auth/me');
    console.log('✅ Current user fetched:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Failed to fetch current user:', error);
    throw error;
  }
}

export function logout() {
  sessionStorage.removeItem('access_token');
  sessionStorage.removeItem('refresh_token');
  window.location.href = '/login';
}

// For development/testing - create a test token using backend test users
export async function createTestToken() {
  try {
    // Use the simplified test credentials from async server:
    // superadmin/superadmin123
    await login('superadmin', 'superadmin123');
    console.log('Successfully logged in with test user credentials (ASYNC)');
    return true;
  } catch (error) {
    console.warn('Test login failed (ASYNC):', error);
    return false;
  }
}

// ASYNC Server API functions (all with /api/v1 prefix)
export async function fetchUsers() {
  try {
    // Try authenticated endpoint first
    const response = await api.get('/users');
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 403 || error.response?.status === 401) {
      console.warn('⚠️ Authentication failed, falling back to test endpoint');
      // Fallback to test endpoint for development
      const testResponse = await api.get('/users/test');
      return testResponse.data;
    }
    throw error;
  }
}

export async function fetchInvoices() {
  const response = await api.get('/invoices');
  return response.data;
}

// Client API functions
export interface Client {
  id: number;
  name: string;
}

export const fetchClients = async (): Promise<Client[]> => {
  const response = await api.get('/clients');
  return response.data;
};

// Role API functions
export interface Role {
  id: number;
  name: string;
  permissions?: any;
}

export const fetchRoles = async (): Promise<Role[]> => {
  const response = await api.get('/roles');
  return response.data;
};

// User CRUD operations for ASYNC server
export const createUser = async (user: any): Promise<any> => {
  console.log('🔧 API.createUser - Starting API call (ASYNC)');
  console.log('📋 Request payload:', {
    ...user,
    password: user.password ? '[PROVIDED]' : '[MISSING]'
  });
  console.log('🔐 Auth headers will be added by interceptor');
  
  try {
  console.log('📡 Making POST request to /user-management/create (ASYNC)...');
  const response = await api.post('/user-management/create', user);
    console.log('✅ API call successful (ASYNC)');
    console.log('📨 Response status:', response.status);
    console.log('📄 Response data:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('❌ API.createUser failed (ASYNC)');
    console.error('📊 Error details:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      headers: error.response?.headers
    });
    
    // Enhanced validation error logging
    if (error.response?.status === 422 && error.response?.data?.detail) {
      console.error('🔍 VALIDATION ERROR DETAILS:');
      if (Array.isArray(error.response.data.detail)) {
        error.response.data.detail.forEach((validationError: any, index: number) => {
          console.error(`❌ Validation Error ${index + 1}:`, {
            field: validationError.loc?.join('.') || 'unknown',
            message: validationError.msg || 'No message',
            type: validationError.type || 'No type',
            input: validationError.input || 'No input shown'
          });
        });
      } else {
        console.error('❌ Validation Error:', error.response.data.detail);
      }
    }
    
    throw error;
  }
};

export const updateUser = async (id: string | number, user: any): Promise<any> => {
  const response = await api.put(`/user-management/${id}`, user);
  return response.data;
};

export const resetUserPassword = async (id: string | number, password: string): Promise<any> => {
  const response = await api.patch(`/user-management/${id}/reset-password`, { password });
  return response.data;
};

export const deleteUser = async (id: string | number): Promise<void> => {
  const response = await api.delete(`/user-management/${id}`);
  return response.data;
};

// Health check for async server
export const checkServerHealth = async () => {
  try {
    const response = await axios.get(`${API_ROOT_URL}/health`);
    console.log('✅ Async server health check passed:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Async server health check failed:', error);
    throw error;
  }
};

// Add more entity-specific API calls as needed
