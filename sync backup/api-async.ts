// ASYNC API service for connecting frontend to the high-performance async backend server
// This connects to the async FastAPI server on port 8001 with Redis caching and enhanced performance
import axios from 'axios';

// Async server configuration - connects to port 8001
const API_BASE_URL_ASYNC = process.env.REACT_APP_API_BASE_URL_ASYNC || 'http://localhost:8001';

export const apiAsync = axios.create({
  baseURL: API_BASE_URL_ASYNC,
  withCredentials: true,
  timeout: 10000, // 10 second timeout for async operations
});

// Add JWT token to requests with async server logging
apiAsync.interceptors.request.use((config) => {
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

// Handle token refresh on 401 errors for async server
apiAsync.interceptors.response.use(
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
          const response = await apiAsync.post('/api/v1/auth/refresh', {
            refresh_token: refreshToken
          });
          const newToken = (response.data as any).access_token;
          sessionStorage.setItem('access_token', newToken);
          // Retry the original request
          if (error.config.headers) {
            error.config.headers.Authorization = `Bearer ${newToken}`;
          }
          return apiAsync.request(error.config);
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
export async function loginAsync(username: string, password: string) {
  try {
    // FastAPI OAuth2PasswordRequestForm expects application/x-www-form-urlencoded
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    
    const response = await apiAsync.post('/api/v1/auth/token', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    const data = response.data as { access_token: string; token_type: string };
    sessionStorage.setItem('access_token', data.access_token);
    sessionStorage.setItem('token_type', data.token_type || 'bearer');
    
    // Decode JWT token to get user information (simple base64 decode of payload)
    try {
      const tokenPayload = data.access_token.split('.')[1];
      const decodedPayload = JSON.parse(atob(tokenPayload));
      const userData = {
        username: decodedPayload.sub,
        role: decodedPayload.role,
        client_id: decodedPayload.client_id,
        user_id: decodedPayload.user_id
      };
      
      console.log('Login successful (ASYNC)', userData);
      return { ...response.data, user: userData };
    } catch (decodeError) {
      console.warn('Could not decode token payload:', decodeError);
      return response.data;
    }
  } catch (error) {
    console.error('Login failed (ASYNC):', error);
    throw error;
  }
}

export function logoutAsync() {
  sessionStorage.removeItem('access_token');
  sessionStorage.removeItem('refresh_token');
  window.location.href = '/login';
}

// For development/testing - create a test token using backend test users
export async function createTestTokenAsync() {
  try {
    // Use the simplified test credentials from async server:
    // superadmin/superadmin123
    await loginAsync('superadmin', 'superadmin123');
    console.log('Successfully logged in with test user credentials (ASYNC)');
    return true;
  } catch (error) {
    console.warn('Test login failed (ASYNC):', error);
    return false;
  }
}

// ASYNC Server API functions (all with /api/v1 prefix)
export async function fetchUsersAsync() {
  const response = await apiAsync.get('/api/v1/users');
  return response.data;
}

export async function fetchInvoicesAsync() {
  const response = await apiAsync.get('/api/v1/invoices');
  return response.data;
}

// Client API functions
export interface Client {
  id: number;
  name: string;
}

export const fetchClientsAsync = async (): Promise<Client[]> => {
  const response = await apiAsync.get('/api/v1/clients');
  return response.data;
};

// Role API functions
export interface Role {
  id: number;
  name: string;
  permissions?: any;
}

export const fetchRolesAsync = async (): Promise<Role[]> => {
  const response = await apiAsync.get('/api/v1/roles');
  return response.data;
};

// Business Units API functions
export const fetchBusinessUnitsAsync = async () => {
  const response = await apiAsync.get('/api/v1/business-units');
  return response.data;
};

// Suppliers API functions
export const fetchSuppliersAsync = async () => {
  const response = await apiAsync.get('/api/v1/suppliers');
  return response.data;
};

// Regions API functions
export const fetchRegionsAsync = async () => {
  const response = await apiAsync.get('/api/v1/regions');
  return response.data;
};

// Currencies API functions
export const fetchCurrenciesAsync = async () => {
  const response = await apiAsync.get('/api/v1/currencies');
  return response.data;
};

// Subcategories API functions
export const fetchSubcategoriesAsync = async () => {
  const response = await apiAsync.get('/api/v1/subcategories');
  return response.data;
};

// Units of Measure API functions
export const fetchUnitsOfMeasureAsync = async () => {
  const response = await apiAsync.get('/api/v1/units-of-measure');
  return response.data;
};

// User CRUD operations for ASYNC server
export const createUserAsync = async (user: any): Promise<any> => {
  console.log('🔧 API.createUserAsync - Starting API call');
  console.log('📋 Request payload:', {
    ...user,
    password: user.password ? '[PROVIDED]' : '[MISSING]'
  });
  console.log('🔐 Auth headers will be added by interceptor');
  
  try {
    console.log('📡 Making POST request to /api/v1/users (ASYNC)...');
    const response = await apiAsync.post('/api/v1/users', user);
    console.log('✅ API call successful (ASYNC)');
    console.log('📨 Response status:', response.status);
    console.log('📄 Response data:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('❌ API.createUserAsync failed');
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

export const updateUserAsync = async (id: string | number, user: any): Promise<any> => {
  const response = await apiAsync.put(`/api/v1/users/${id}`, user);
  return response.data;
};

export const resetUserPasswordAsync = async (id: string | number, password: string): Promise<any> => {
  const response = await apiAsync.patch(`/api/v1/users/${id}/password`, { password });
  return response.data;
};

export const deleteUserAsync = async (id: string | number): Promise<void> => {
  const response = await apiAsync.delete(`/api/v1/users/${id}`);
  return response.data;
};

// Enhanced async server functions with additional endpoints
export const fetchAuditLogsAsync = async () => {
  const response = await apiAsync.get('/api/v1/audit-logs');
  return response.data;
};

export const fetchClientSettingsAsync = async () => {
  const response = await apiAsync.get('/api/v1/client-settings');
  return response.data;
};

export const fetchImportErrorsAsync = async () => {
  const response = await apiAsync.get('/api/v1/import-errors');
  return response.data;
};

export const fetchInvoiceItemsAsync = async () => {
  const response = await apiAsync.get('/api/v1/invoice-items');
  return response.data;
};

export const fetchScreenPermissionsAsync = async () => {
  const response = await apiAsync.get('/api/v1/screen-permissions');
  return response.data;
};

export const fetchReportsAsync = async () => {
  const response = await apiAsync.get('/api/v1/reports');
  return response.data;
};

// Health check for async server
export const checkAsyncServerHealth = async () => {
  try {
    const response = await apiAsync.get('/health');
    console.log('✅ Async server health check passed:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Async server health check failed:', error);
    throw error;
  }
};