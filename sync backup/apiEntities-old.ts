// UPDATED: API entities now connect to ASYNC backend server for enhanced performance
// Original sync server backup available in apiEntities-sync-backup.ts

import { api } from './api';

// ImportErrors
export async function fetchImportErrorsSync() {
  const response = await api.get('/import-errors');
  return response.data;
}
// ImportErrors
export async function createImportErrorSync(data: any) {
  const response = await api.post('/import-errors', data);
  return response.data;
}
export async function updateImportErrorSync(id: string | number, data: any) {
  const response = await api.put(`/import-errors/${id}`, data);
  return response.data;
}
export async function deleteImportErrorSync(id: string | number) {
  const response = await api.delete(`/import-errors/${id}`);
  return response.data;
}
// Settings
export async function fetchSettingsSync() {
  const response = await api.get('/settings');
  return response.data;
}
export async function createSettingSync(data: any) {
  const response = await api.post('/settings', data);
  return response.data;
}
export async function updateSettingSync(id: string | number, data: any) {
  const response = await api.put(`/settings/${id}`, data);
  return response.data;
}
export async function deleteSettingSync(id: string | number) {
  const response = await api.delete(`/settings/${id}`);
  return response.data;
}

// ClientSettings
export async function fetchClientSettingsSync() {
  const response = await api.get('/settings');
  return response.data;
}
export async function createClientSettingSync(data: any) {
  const response = await api.post('/settings', data);
  return response.data;
}
export async function updateClientSettingSync(id: string | number, data: any) {
  const response = await api.put(`/settings/${id}`, data);
  return response.data;
}
export async function deleteClientSettingSync(id: string | number) {
  const response = await api.delete(`/settings/${id}`);
  return response.data;
}

// ScreenPermissions
export async function fetchScreenPermissionsSync() {
  const response = await api.get('/screen-permissions');
  return response.data;
}
export async function createScreenPermissionSync(data: any) {
  const response = await api.post('/screen-permissions', data);
  return response.data;
}
export async function updateScreenPermissionSync(id: string | number, data: any) {
  const response = await api.put(`/screen-permissions/${id}`, data);
  return response.data;
}
export async function deleteScreenPermissionSync(id: string | number) {
  const response = await api.delete(`/screen-permissions/${id}`);
  return response.data;
}

// InvoiceItems
export async function fetchInvoiceItemsSync() {
  const response = await api.get('/invoice-items');
  return response.data;
}
export async function createInvoiceItemSync(data: any) {
  const response = await api.post('/invoice-items', data);
  return response.data;
}
export async function updateInvoiceItemSync(id: string | number, data: any) {
  const response = await api.put(`/invoice-items/${id}`, data);
  return response.data;
}
export async function deleteInvoiceItemSync(id: string | number) {
  const response = await api.delete(`/invoice-items/${id}`);
  return response.data;
}

// AuditLogs
export async function fetchAuditLogsSync() {
  const response = await api.get('/audit-logs');
  return response.data;
}
export async function createAuditLogSync(data: any) {
  const response = await api.post('/audit-logs', data);
  return response.data;
}
export async function updateAuditLogSync(id: string | number, data: any) {
  const response = await api.put(`/audit-logs/${id}`, data);
  return response.data;
}
export async function deleteAuditLogSync(id: string | number) {
  const response = await api.delete(`/audit-logs/${id}`);
  return response.data;
}

// BusinessUnits
export async function fetchBusinessUnitsSync() {
  const response = await api.get('/business-units');
  return response.data;
}
export async function createBusinessUnitSync(data: any) {
  const response = await api.post('/business-units', data);
  return response.data;
}
export async function updateBusinessUnitSync(id: string | number, data: any) {
  const response = await api.put(`/business-units/${id}`, data);
  return response.data;
}
export async function deleteBusinessUnitSync(id: string | number) {
  const response = await api.delete(`/business-units/${id}`);
  return response.data;
}

// Suppliers
export async function fetchSuppliersSync() {
  const response = await api.get('/suppliers');
  return response.data;
}
export async function createSupplierSync(data: any) {
  const response = await api.post('/suppliers', data);
  return response.data;
}
export async function updateSupplierSync(id: string | number, data: any) {
  const response = await api.put(`/suppliers/${id}`, data);
  return response.data;
}
export async function deleteSupplierSync(id: string | number) {
  const response = await api.delete(`/suppliers/${id}`);
  return response.data;
}

// Currencies
export async function fetchCurrenciesSync() {
  const response = await api.get('/currencies');
  return response.data;
}
export async function createCurrencySync(data: any) {
  const response = await api.post('/currencies', data);
  return response.data;
}
export async function updateCurrencySync(id: string | number, data: any) {
  const response = await api.put(`/currencies/${id}`, data);
  return response.data;
}
export async function deleteCurrencySync(id: string | number) {
  const response = await api.delete(`/currencies/${id}`);
  return response.data;
}

// Regions  
export async function fetchRegionsSync() {
  const response = await api.get('/regions');
  return response.data;
}
export async function createRegionSync(data: any) {
  const response = await api.post('/regions', data);
  return response.data;
}
export async function updateRegionSync(id: string | number, data: any) {
  const response = await api.put(`/regions/${id}`, data);
  return response.data;
}
export async function deleteRegionSync(id: string | number) {
  const response = await api.delete(`/regions/${id}`);
  return response.data;
}

// Subcategories
export async function fetchSubcategoriesSync() {
  const response = await api.get('/subcategories');
  return response.data;
}
export async function createSubcategorySync(data: any) {
  const response = await api.post('/subcategories', data);
  return response.data;
}
export async function updateSubcategorySync(id: string | number, data: any) {
  const response = await api.put(`/subcategories/${id}`, data);
  return response.data;
}
export async function deleteSubcategorySync(id: string | number) {
  const response = await api.delete(`/subcategories/${id}`);
  return response.data;
}

// Units of Measure
export async function fetchUnitsOfMeasureSync() {
  const response = await api.get('/units-of-measure');
  return response.data;
}
export async function createUnitOfMeasureSync(data: any) {
  const response = await api.post('/units-of-measure', data);
  return response.data;
}
export async function updateUnitOfMeasureSync(id: string | number, data: any) {
  const response = await api.put(`/units-of-measure/${id}`, data);
  return response.data;
}
export async function deleteUnitOfMeasureSync(id: string | number) {
  const response = await api.delete(`/units-of-measure/${id}`);
  return response.data;
}

// User Management
export async function fetchUserManagementSync() {
  const response = await api.get('/user-management');
  return response.data;
}
export async function createUserManagementSync(data: any) {
  const response = await api.post('/user-management', data);
  return response.data;
}
export async function updateUserManagementSync(id: string | number, data: any) {
  const response = await api.put(`/user-management/${id}`, data);
  return response.data;
}
export async function deleteUserManagementSync(id: string | number) {
  const response = await api.delete(`/user-management/${id}`);
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

// Invoices
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

// Reports
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