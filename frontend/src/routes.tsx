import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './screens/Dashboard';
import LoginScreen from './screens/LoginScreen';
import ProtectedRoute from './components/ProtectedRoute';
import { useAuth } from './contexts/AuthContext';
import Invoices from './screens/Invoices';
import InvoiceDetail from './screens/InvoiceDetail';
import InvoiceEdit from './screens/InvoiceEdit';
import Suppliers from './screens/Suppliers';
import SupplierDetail from './screens/SupplierDetail';
import SupplierEdit from './screens/SupplierEdit';
import BusinessUnits from './screens/BusinessUnits';
import BusinessUnitDetail from './screens/BusinessUnitDetail';
import BusinessUnitEdit from './screens/BusinessUnitEdit';
import Regions from './screens/Regions';
import RegionDetail from './screens/RegionDetail';
import RegionEdit from './screens/RegionEdit';
import Roles from './screens/Roles';
import RoleDetail from './screens/RoleDetail';
import RoleEdit from './screens/RoleEdit';
import Users from './screens/Users';
import UserDetail from './screens/UserDetail';
import UserEdit from './screens/UserEdit';
import Clients from './screens/Clients';
import ClientDetail from './screens/ClientDetail';
import ClientEdit from './screens/ClientEdit';
import Subcategories from './screens/Subcategories';
import SubcategoryDetail from './screens/SubcategoryDetail';
import SubcategoryEdit from './screens/SubcategoryEdit';
import UnitOfMeasure from './screens/UnitOfMeasure';
import UnitOfMeasureDetail from './screens/UnitOfMeasureDetail';
import UnitOfMeasureEdit from './screens/UnitOfMeasureEdit';
import Currency from './screens/Currency';
import CurrencyDetail from './screens/CurrencyDetail';
import CurrencyEdit from './screens/CurrencyEdit';
import ImportErrors from './screens/ImportErrors';
import Reporting from './screens/Reporting';
import ClientSettings from './screens/ClientSettings';
import Settings from './screens/Settings';
import ScreenPermissions from './screens/ScreenPermissions';

export default function AppRoutes() {
  const { isAuthenticated, login } = useAuth();

  return (
    <Routes>
      {/* Public routes */}
      <Route 
        path="/login" 
        element={
          isAuthenticated ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <LoginScreen onLoginSuccess={login} />
          )
        } 
      />
      
      {/* Protected routes */}
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <Navigate to="/dashboard" replace />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute screenRoute="/dashboard">
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Invoice routes */}
      <Route 
        path="/invoices" 
        element={
          <ProtectedRoute screenRoute="/invoices">
            <Invoices />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/invoices/:id" 
        element={
          <ProtectedRoute screenRoute="/invoices">
            <InvoiceDetail />
          </ProtectedRoute>
        } 
      />  
      <Route 
        path="/invoices/:id/edit" 
        element={
          <ProtectedRoute screenRoute="/invoices">
            <InvoiceEdit />
          </ProtectedRoute>
        } 
      />
      
      {/* Supplier routes */}
      <Route 
        path="/suppliers" 
        element={
          <ProtectedRoute>
            <Suppliers />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/suppliers/:id" 
        element={
          <ProtectedRoute>
            <SupplierDetail />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/suppliers/:id/edit" 
        element={
          <ProtectedRoute>
            <SupplierEdit />
          </ProtectedRoute>
        } 
      />
      
      {/* Business Unit routes */}
      <Route 
        path="/business-units" 
        element={
          <ProtectedRoute>
            <BusinessUnits />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/business-units/:id" 
        element={
          <ProtectedRoute>
            <BusinessUnitDetail />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/business-units/:id/edit" 
        element={
          <ProtectedRoute>
            <BusinessUnitEdit />
          </ProtectedRoute>
        } 
      />
      
      {/* Region routes */}
      <Route 
        path="/regions" 
        element={
          <ProtectedRoute>
            <Regions />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/regions/:id" 
        element={
          <ProtectedRoute>
            <RegionDetail />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/regions/:id/edit" 
        element={
          <ProtectedRoute>
            <RegionEdit />
          </ProtectedRoute>
        } 
      />
      
      {/* Admin-only routes */}
      <Route 
        path="/roles" 
        element={
          <ProtectedRoute screenRoute="/roles">
            <Roles />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/roles/:id" 
        element={
          <ProtectedRoute screenRoute="/roles">
            <RoleDetail />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/roles/:id/edit" 
        element={
          <ProtectedRoute requiredRoles={['client_admin', 'superadmin']}>
            <RoleEdit />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/users" 
        element={
          <ProtectedRoute screenRoute="/users">
            <Users />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/users/:id" 
        element={
          <ProtectedRoute screenRoute="/users">
            <UserDetail />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/users/:id/edit" 
        element={
          <ProtectedRoute screenRoute="/users">
            <UserEdit />
          </ProtectedRoute>
        } 
      />
      
      {/* Super admin only routes */}
      <Route 
        path="/clients" 
        element={
          <ProtectedRoute requiredRoles={['superadmin']}>
            <Clients />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/clients/:id" 
        element={
          <ProtectedRoute requiredRoles={['superadmin']}>
            <ClientDetail />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/clients/:id/edit" 
        element={
          <ProtectedRoute requiredRoles={['superadmin']}>
            <ClientEdit />
          </ProtectedRoute>
        } 
      />
      
      {/* Other protected routes */}
      <Route 
        path="/subcategories" 
        element={
          <ProtectedRoute>
            <Subcategories />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/subcategories/:id" 
        element={
          <ProtectedRoute>
            <SubcategoryDetail />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/subcategories/:id/edit" 
        element={
          <ProtectedRoute>
            <SubcategoryEdit />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/unit-of-measure" 
        element={
          <ProtectedRoute>
            <UnitOfMeasure />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/unit-of-measure/:id" 
        element={
          <ProtectedRoute>
            <UnitOfMeasureDetail />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/unit-of-measure/:id/edit" 
        element={
          <ProtectedRoute>
            <UnitOfMeasureEdit />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/currency" 
        element={
          <ProtectedRoute>
            <Currency />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/currency/:id" 
        element={
          <ProtectedRoute>
            <CurrencyDetail />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/currency/:id/edit" 
        element={
          <ProtectedRoute>
            <CurrencyEdit />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/import-errors" 
        element={
          <ProtectedRoute>
            <ImportErrors />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/reporting" 
        element={
          <ProtectedRoute>
            <Reporting />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/client-settings" 
        element={
          <ProtectedRoute requiredRoles={['client_admin', 'superadmin']}>
            <ClientSettings />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/settings" 
        element={
          <ProtectedRoute>
            <Settings />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/screen-permissions" 
        element={
          <ProtectedRoute screenRoute="/screen-permissions">
            <ScreenPermissions />
          </ProtectedRoute>
        } 
      />
    </Routes>
  );
}
