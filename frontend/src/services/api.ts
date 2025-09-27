// Example API service for connecting frontend to backend APIs
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

// Add JWT token to requests
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('access_token');
  
  // Log all outgoing requests for debugging
  console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
  console.log('📋 Request data:', config.data);
  
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log('🔐 Auth token added to request');
    
    // Decode and log token info (for debugging)
    try {
      const tokenPayload = token.split('.')[1];
      const decodedPayload = JSON.parse(atob(tokenPayload));
      console.log('👤 Token user info:', {
        username: decodedPayload.sub,
        role: decodedPayload.role,
        client_id: decodedPayload.client_id,
        exp: new Date(decodedPayload.exp * 1000)
      });
    } catch (e) {
      console.warn('⚠️ Could not decode token for debugging');
    }
  } else {
    console.warn('🔐 No auth token found - API calls may fail');
    if (process.env.NODE_ENV === 'development') {
      console.warn('🔧 Development mode: Consider implementing auto-login for testing');
    }
  }
  return config;
});

// Handle token refresh on 401 errors
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`);
    return response;
  },
  async (error) => {
    console.error(`❌ API Error: ${error.response?.status} ${error.config?.method?.toUpperCase()} ${error.config?.url}`);
    console.error('📄 Error response data:', error.response?.data);
    
    if (error.response?.status === 401) {
      console.warn('🚫 401 Unauthorized - attempting token refresh...');
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

// Auth functions
export async function login(username: string, password: string) {
  try {
    // FastAPI OAuth2PasswordRequestForm expects application/x-www-form-urlencoded
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    
    const response = await api.post('/token', params, {
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
      
      console.log('Login successful', userData);
      return { ...response.data, user: userData };
    } catch (decodeError) {
      console.warn('Could not decode token payload:', decodeError);
      return response.data;
    }
  } catch (error) {
    console.error('Login failed:', error);
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
    // Use one of the test users from your backend:
    // superadmin/superadmin123, clientadmin/clientadmin123, user/user123
    await login('user', 'user123');
    console.log('Successfully logged in with test user credentials');
    return true;
  } catch (error) {
    console.warn('Test login failed:', error);
    return false;
  }
}

// Example: Fetch all users
export async function fetchUsers() {
  const response = await api.get('/users');
  return response.data;
}

// Example: Fetch all invoices
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

// User CRUD operations
export const createUser = async (user: any): Promise<any> => {
  console.log('🔧 API.createUser - Starting API call');
  console.log('📋 Request payload:', {
    ...user,
    password: user.password ? '[PROVIDED]' : '[MISSING]'
  });
  console.log('🔐 Auth headers will be added by interceptor');
  
  try {
    console.log('📡 Making POST request to /users...');
    const response = await api.post('/users', user);
    console.log('✅ API call successful');
    console.log('📨 Response status:', response.status);
    console.log('📄 Response data:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('❌ API.createUser failed');
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
  const response = await api.put(`/users/${id}`, user);
  return response.data;
};

export const resetUserPassword = async (id: string | number, password: string): Promise<any> => {
  const response = await api.patch(`/users/${id}/password`, { password });
  return response.data;
};

export const deleteUser = async (id: string | number): Promise<void> => {
  const response = await api.delete(`/users/${id}`);
  return response.data;
};

// Add more entity-specific API calls as needed
