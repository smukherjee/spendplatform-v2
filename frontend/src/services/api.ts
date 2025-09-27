// Example API service for connecting frontend to backend APIs
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

// Add JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Try to refresh token or redirect to login
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await api.post('/auth/refresh', {
            refresh_token: refreshToken
          });
          const newToken = (response.data as any).access_token;
          localStorage.setItem('access_token', newToken);
          // Retry the original request
          if (error.config.headers) {
            error.config.headers.Authorization = `Bearer ${newToken}`;
          }
          return api.request(error.config);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      } else {
        // No refresh token, redirect to login
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth functions
export async function login(username: string, password: string) {
  try {
    // FastAPI OAuth2PasswordRequestForm expects form-data, not JSON
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await api.post('/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    const data = response.data as { access_token: string; token_type: string };
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('token_type', data.token_type || 'bearer');
    
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
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/login';
}

// For development/testing - create a test token using backend test users
export async function createTestToken() {
  try {
    // Use one of the test users from your backend:
    // superadmin/superadminpw, clientadmin/clientadminpw, user/userpw
    await login('user', 'userpw');
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

// Add more entity-specific API calls as needed
