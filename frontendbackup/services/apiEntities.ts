// ImportErrors
export async function fetchImportErrors() {
  const response = await api.get('/import-errors');
  return response.data;
}
export async function createImportError(data: any) {
  const response = await api.post('/import-errors', data);
  return response.data;
}
export async function updateImportError(id: string | number, data: any) {
  const response = await api.put(`/import-errors/${id}`, data);
  return response.data;
}
export async function deleteImportError(id: string | number) {
  const response = await api.delete(`/import-errors/${id}`);
  return response.data;
}
// Settings
export async function fetchSettings() {
  const response = await api.get('/settings');
  return response.data;
}
export async function createSetting(data: any) {
  const response = await api.post('/settings', data);
  return response.data;
}
export async function updateSetting(id: string | number, data: any) {
  const response = await api.put(`/settings/${id}`, data);
  return response.data;
}
export async function deleteSetting(id: string | number) {
  const response = await api.delete(`/settings/${id}`);
  return response.data;
}

// ClientSettings
export async function fetchClientSettings() {
  const response = await api.get('/client-settings');
  return response.data;
}
export async function createClientSetting(data: any) {
  const response = await api.post('/client-settings', data);
  return response.data;
}
export async function updateClientSetting(id: string | number, data: any) {
  const response = await api.put(`/client-settings/${id}`, data);
  return response.data;
}
export async function deleteClientSetting(id: string | number) {
  const response = await api.delete(`/client-settings/${id}`);
  return response.data;
}
import { api } from './api';

// Business Units
export async function fetchBusinessUnits() {
  const response = await api.get('/business-units');
  return response.data;
}
export async function createBusinessUnit(data: any) {
  const response = await api.post('/business-units', data);
  return response.data;
}
export async function updateBusinessUnit(id: string | number, data: any) {
  const response = await api.put(`/business-units/${id}`, data);
  return response.data;
}
export async function deleteBusinessUnit(id: string | number) {
  const response = await api.delete(`/business-units/${id}`);
  return response.data;
}

// Repeat for other entities (Invoices, Suppliers, Regions, etc.)
export async function fetchInvoices() {
  const response = await api.get('/invoices');
  return response.data;
}
export async function createInvoice(data: any) {
  const response = await api.post('/invoices', data);
  return response.data;
}
export async function updateInvoice(id: string | number, data: any) {
  const response = await api.put(`/invoices/${id}`, data);
  return response.data;
}
export async function deleteInvoice(id: string | number) {
  const response = await api.delete(`/invoices/${id}`);
  return response.data;
}

export async function fetchSuppliers() {
  const response = await api.get('/suppliers');
  return response.data;
}
export async function createSupplier(data: any) {
  const response = await api.post('/suppliers', data);
  return response.data;
}
export async function updateSupplier(id: string | number, data: any) {
  const response = await api.put(`/suppliers/${id}`, data);
  return response.data;
}
export async function deleteSupplier(id: string | number) {
  const response = await api.delete(`/suppliers/${id}`);
  return response.data;
}

// Regions
export async function fetchRegions() {
  const response = await api.get('/regions');
  return response.data;
}
export async function createRegion(data: any) {
  const response = await api.post('/regions', data);
  return response.data;
}
export async function updateRegion(id: string | number, data: any) {
  const response = await api.put(`/regions/${id}`, data);
  return response.data;
}
export async function deleteRegion(id: string | number) {
  const response = await api.delete(`/regions/${id}`);
  return response.data;
}

// Roles
export async function fetchRoles() {
  const response = await api.get('/roles');
  return response.data;
}
export async function createRole(data: any) {
  const response = await api.post('/roles', data);
  return response.data;
}
export async function updateRole(id: string | number, data: any) {
  const response = await api.put(`/roles/${id}`, data);
  return response.data;
}
export async function deleteRole(id: string | number) {
  const response = await api.delete(`/roles/${id}`);
  return response.data;
}

// Users
export async function fetchUsers() {
  const response = await api.get('/users');
  return response.data;
}
export async function createUser(data: any) {
  const response = await api.post('/users', data);
  return response.data;
}
export async function updateUser(id: string | number, data: any) {
  const response = await api.put(`/users/${id}`, data);
  return response.data;
}
export async function deleteUser(id: string | number) {
  const response = await api.delete(`/users/${id}`);
  return response.data;
}

// Clients
export async function fetchClients() {
  const response = await api.get('/clients');
  return response.data;
}
export async function createClient(data: any) {
  const response = await api.post('/clients', data);
  return response.data;
}
export async function updateClient(id: string | number, data: any) {
  const response = await api.put(`/clients/${id}`, data);
  return response.data;
}
export async function deleteClient(id: string | number) {
  const response = await api.delete(`/clients/${id}`);
  return response.data;
}

// Subcategories
export async function fetchSubcategories() {
  const response = await api.get('/subcategories');
  return response.data;
}
export async function createSubcategory(data: any) {
  const response = await api.post('/subcategories', data);
  return response.data;
}
export async function updateSubcategory(id: string | number, data: any) {
  const response = await api.put(`/subcategories/${id}`, data);
  return response.data;
}
export async function deleteSubcategory(id: string | number) {
  const response = await api.delete(`/subcategories/${id}`);
  return response.data;
}

// UnitOfMeasure
export async function fetchUnitOfMeasures() {
  const response = await api.get('/unit-of-measure');
  return response.data;
}
export async function createUnitOfMeasure(data: any) {
  const response = await api.post('/unit-of-measure', data);
  return response.data;
}
export async function updateUnitOfMeasure(id: string | number, data: any) {
  const response = await api.put(`/unit-of-measure/${id}`, data);
  return response.data;
}
export async function deleteUnitOfMeasure(id: string | number) {
  const response = await api.delete(`/unit-of-measure/${id}`);
  return response.data;
}

// Currency
export async function fetchCurrencies() {
  const response = await api.get('/currency');
  return response.data;
}
export async function createCurrency(data: any) {
  const response = await api.post('/currency', data);
  return response.data;
}
export async function updateCurrency(id: string | number, data: any) {
  const response = await api.put(`/currency/${id}`, data);
  return response.data;
}
export async function deleteCurrency(id: string | number) {
  const response = await api.delete(`/currency/${id}`);
  return response.data;
}


// Reporting
export async function fetchReports() {
  const response = await api.get('/reports');
  return response.data;
}
export async function createReport(data: any) {
  const response = await api.post('/reports', data);
  return response.data;
}
export async function updateReport(id: string | number, data: any) {
  const response = await api.put(`/reports/${id}`, data);
  return response.data;
}
export async function deleteReport(id: string | number) {
  const response = await api.delete(`/reports/${id}`);
  return response.data;
}
