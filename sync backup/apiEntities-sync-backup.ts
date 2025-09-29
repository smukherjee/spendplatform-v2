// BACKUP: Original sync API entities service
// This is a backup of the original apiEntities.ts file that connects to the sync server
// Created as backup before switching to async server configuration

import { apiSync as api } from './api-sync-backup';

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