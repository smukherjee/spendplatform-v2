// API entities for async backend server (port 8001)
import { api } from './api';

// Authentication
export async function login(credentials: { username: string; password: string }) {
  const response = await api.post('/auth/login', credentials);
  return response.data;
}

// Roles
export async function fetchRoles() {
  const response = await api.get('/roles/');
  return response.data;
}

export async function createRole(data: any) {
  const response = await api.post('/roles/', data);
  return response.data;
}

export async function deleteRole(id: string | number) {
  const response = await api.delete(`/roles/${id}`);
  return response.data;
}

// Import Errors
export async function fetchImportErrors(params?: any) {
  const response = await api.get('/import-errors', { params });
  return response.data;
}

export async function createImportError(data: any) {
  const response = await api.post('/import-errors', data);
  return response.data;
}

export async function deleteImportError(id: string | number) {
  const response = await api.delete(`/import-errors/${id}`);
  return response.data;
}

// Settings
export async function fetchSettings() {
  const response = await api.get('/settings/');
  return response.data;
}

export async function createSetting(data: any) {
  const response = await api.post('/settings/', data);
  return response.data;
}

export async function deleteSetting(id: string | number) {
  const response = await api.delete(`/settings/${id}`);
  return response.data;
}

// Client Settings
export async function fetchClientSettings() {
  const response = await api.get('/client-settings/');
  return response.data;
}

export async function createClientSetting(data: any) {
  const response = await api.post('/client-settings/', data);
  return response.data;
}

export async function deleteClientSetting(id: string | number) {
  const response = await api.delete(`/client-settings/${id}`);
  return response.data;
}

// Currencies
export async function fetchCurrencies() {
  const response = await api.get('/currencies/');
  return response.data;
}

export async function createCurrency(data: any) {
  const response = await api.post('/currencies/', data);
  return response.data;
}

export async function deleteCurrency(id: string | number) {
  const response = await api.delete(`/currencies/${id}`);
  return response.data;
}

// Regions
export async function fetchRegions() {
  const response = await api.get('/regions/');
  return response.data;
}

export async function createRegion(data: any) {
  const response = await api.post('/regions/', data);
  return response.data;
}

export async function deleteRegion(id: string | number) {
  const response = await api.delete(`/regions/${id}`);
  return response.data;
}

// Suppliers
export async function fetchSuppliers(params?: any) {
  const response = await api.get('/suppliers/', { params });
  return response.data;
}

export async function createSupplier(data: any) {
  const response = await api.post('/suppliers/', data);
  return response.data;
}

export async function deleteSupplier(id: string | number) {
  const response = await api.delete(`/suppliers/${id}`);
  return response.data;
}

// Business Units
export async function fetchBusinessUnits() {
  const response = await api.get('/business-units/');
  return response.data;
}

export async function createBusinessUnit(data: any) {
  const response = await api.post('/business-units/', data);
  return response.data;
}

export async function deleteBusinessUnit(id: string | number) {
  const response = await api.delete(`/business-units/${id}`);
  return response.data;
}

// Subcategories
export async function fetchSubcategories() {
  const response = await api.get('/subcategories/');
  return response.data;
}

export async function createSubcategory(data: any) {
  const response = await api.post('/subcategories/', data);
  return response.data;
}

export async function deleteSubcategory(id: string | number) {
  const response = await api.delete(`/subcategories/${id}`);
  return response.data;
}

// Unit of Measure
export async function fetchUnitOfMeasures() {
  const response = await api.get('/units-of-measure/');
  return response.data;
}

export async function createUnitOfMeasure(data: any) {
  const response = await api.post('/units-of-measure/', data);
  return response.data;
}

export async function deleteUnitOfMeasure(id: string | number) {
  const response = await api.delete(`/units-of-measure/${id}`);
  return response.data;
}

// User Management
export async function fetchUserManagement(params?: any) {
  const response = await api.get('/user-management/', { params });
  return response.data;
}

export async function createUser(data: any) {
  const response = await api.post('/user-management/create', data);
  return response.data;
}

export async function deleteUserManagement(id: string | number) {
  const response = await api.delete(`/user-management/${id}`);
  return response.data;
}

// Invoices
export async function fetchInvoices(params?: any) {
  const response = await api.get('/invoices/', { params });
  return response.data;
}

export async function createInvoice(data: any) {
  const response = await api.post('/invoices/', data);
  return response.data;
}

export async function deleteInvoice(id: string | number) {
  const response = await api.delete(`/invoices/${id}`);
  return response.data;
}

// Clients
export async function fetchClients() {
  const response = await api.get('/clients/');
  return response.data;
}

export async function createClient(data: any) {
  const response = await api.post('/clients/', data);
  return response.data;
}

export async function deleteClient(id: string | number) {
  const response = await api.delete(`/clients/${id}`);
  return response.data;
}

// Reports
export async function fetchReports() {
  const response = await api.get('/reports/');
  return response.data;
}

export async function createReport(data: any) {
  const response = await api.post('/reports/', data);
  return response.data;
}

export async function deleteReport(id: string | number) {
  const response = await api.delete(`/reports/${id}`);
  return response.data;
}

// Screen Permissions
export async function fetchScreenPermissions() {
  const response = await api.get('/screen-permissions/');
  return response.data;
}

export async function createScreenPermission(data: any) {
  const response = await api.post('/screen-permissions/', data);
  return response.data;
}

export async function deleteScreenPermission(id: string | number) {
  const response = await api.delete(`/screen-permissions/${id}`);
  return response.data;
}
