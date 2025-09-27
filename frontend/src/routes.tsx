import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './screens/Dashboard.tsx';
import LoginScreen from './screens/LoginScreen.tsx';
import ProtectedRoute from './components/ProtectedRoute.tsx';
import { useAuth } from './contexts/AuthContext.tsx';
import Invoices from './screens/Invoices.tsx';
import InvoiceDetail from './screens/InvoiceDetail.tsx';
import InvoiceEdit from './screens/InvoiceEdit.tsx';
import Suppliers from './screens/Suppliers.tsx';
import SupplierDetail from './screens/SupplierDetail.tsx';
import SupplierEdit from './screens/SupplierEdit.tsx';
import BusinessUnits from './screens/BusinessUnits.tsx';
import BusinessUnitDetail from './screens/BusinessUnitDetail.tsx';
import BusinessUnitEdit from './screens/BusinessUnitEdit.tsx';
import Regions from './screens/Regions.tsx';
import RegionDetail from './screens/RegionDetail.tsx';
import RegionEdit from './screens/RegionEdit.tsx';
import Roles from './screens/Roles.tsx';
import RoleDetail from './screens/RoleDetail.tsx';
import RoleEdit from './screens/RoleEdit.tsx';
import Users from './screens/Users.tsx';
import UserDetail from './screens/UserDetail.tsx';
import UserEdit from './screens/UserEdit.tsx';
import Clients from './screens/Clients.tsx';
import ClientDetail from './screens/ClientDetail.tsx';
import ClientEdit from './screens/ClientEdit.tsx';
import Subcategories from './screens/Subcategories.tsx';
import SubcategoryDetail from './screens/SubcategoryDetail.tsx';
import SubcategoryEdit from './screens/SubcategoryEdit.tsx';
import UnitOfMeasure from './screens/UnitOfMeasure.tsx';
import UnitOfMeasureDetail from './screens/UnitOfMeasureDetail.tsx';
import UnitOfMeasureEdit from './screens/UnitOfMeasureEdit.tsx';
import Currency from './screens/Currency.tsx';
import CurrencyDetail from './screens/CurrencyDetail.tsx';
import CurrencyEdit from './screens/CurrencyEdit.tsx';
import ImportErrors from './screens/ImportErrors.tsx';
import Reporting from './screens/Reporting.tsx';
import ClientSettings from './screens/ClientSettings.tsx';
import Settings from './screens/Settings.tsx';

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
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Invoice routes */}
      <Route 
        path="/invoices" 
        element={
          <ProtectedRoute>
            <Invoices />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/invoices/:id" 
        element={
          <ProtectedRoute>
            <InvoiceDetail />
          </ProtectedRoute>
        } 
      />  
      <Route 
        path="/invoices/:id/edit" 
        element={
          <ProtectedRoute>
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
          <ProtectedRoute requiredRoles={['client_admin', 'superadmin']}>
            <Roles />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/roles/:id" 
        element={
          <ProtectedRoute requiredRoles={['client_admin', 'superadmin']}>
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
          <ProtectedRoute requiredRoles={['client_admin', 'superadmin']}>
            <Users />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/users/:id" 
        element={
          <ProtectedRoute requiredRoles={['client_admin', 'superadmin']}>
            <UserDetail />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/users/:id/edit" 
        element={
          <ProtectedRoute requiredRoles={['client_admin', 'superadmin']}>
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
    </Routes>
  );
}
