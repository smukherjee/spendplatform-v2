// Example API service for connecting frontend to backend APIs
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

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
