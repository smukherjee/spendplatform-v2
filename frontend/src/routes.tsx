import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginScreen from './screens/LoginScreen';
import ProtectedRoute from './components/ProtectedRoute';
import { useAuth } from './contexts/AuthContext';
import ErrorBoundary from './ErrorBoundary';

// Lazy load heavy components to reduce initial bundle size
const Dashboard = lazy(() => import('./screens/Dashboard'));
const Invoices = lazy(() => import('./screens/Invoices'));
const InvoiceDetail = lazy(() => import('./screens/InvoiceDetail'));
const InvoiceEdit = lazy(() => import('./screens/InvoiceEdit'));
const Suppliers = lazy(() => import('./screens/Suppliers'));
const SupplierDetail = lazy(() => import('./screens/SupplierDetail'));
const SupplierEdit = lazy(() => import('./screens/SupplierEdit'));
const BusinessUnits = lazy(() => import('./screens/BusinessUnits'));
const BusinessUnitDetail = lazy(() => import('./screens/BusinessUnitDetail'));
const BusinessUnitEdit = lazy(() => import('./screens/BusinessUnitEdit'));
const Regions = lazy(() => import('./screens/Regions'));
const RegionDetail = lazy(() => import('./screens/RegionDetail'));
const RegionEdit = lazy(() => import('./screens/RegionEdit'));
const Roles = lazy(() => import('./screens/Roles'));
const RoleDetail = lazy(() => import('./screens/RoleDetail'));
const RoleEdit = lazy(() => import('./screens/RoleEdit'));
const Users = lazy(() => import('./screens/Users'));
const UserDetail = lazy(() => import('./screens/UserDetail'));
const UserEdit = lazy(() => import('./screens/UserEdit'));
const Clients = lazy(() => import('./screens/Clients'));
const ClientDetail = lazy(() => import('./screens/ClientDetail'));
const ClientEdit = lazy(() => import('./screens/ClientEdit'));
const Subcategories = lazy(() => import('./screens/Subcategories'));
const SubcategoryDetail = lazy(() => import('./screens/SubcategoryDetail'));
const SubcategoryEdit = lazy(() => import('./screens/SubcategoryEdit'));
const UnitOfMeasure = lazy(() => import('./screens/UnitOfMeasure'));
const UnitOfMeasureDetail = lazy(() => import('./screens/UnitOfMeasureDetail'));
const UnitOfMeasureEdit = lazy(() => import('./screens/UnitOfMeasureEdit'));
const Currency = lazy(() => import('./screens/Currency'));
const CurrencyDetail = lazy(() => import('./screens/CurrencyDetail'));
const CurrencyEdit = lazy(() => import('./screens/CurrencyEdit'));
const ImportErrors = lazy(() => import('./screens/ImportErrors'));
const Reporting = lazy(() => import('./screens/Reporting'));
const ClientSettings = lazy(() => import('./screens/ClientSettings'));
const Settings = lazy(() => import('./screens/Settings'));
const ScreenPermissions = lazy(() => import('./screens/ScreenPermissions'));

// Loading component with better UX
const PageLoader = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    minHeight: '200px',
    color: '#666'
  }}>
    <div>
      <div style={{ 
        width: '40px', 
        height: '40px', 
        border: '3px solid #f3f3f3',
        borderTop: '3px solid #3498db',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        margin: '0 auto 10px'
      }} />
      <div>Loading...</div>
    </div>
  </div>
);

export default function AppRoutes() {
  const { isAuthenticated, login } = useAuth();

  return (
    <ErrorBoundary>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Public routes - no lazy loading for critical paths */}
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
      
      {/* 404 fallback */}
      <Route 
        path="*" 
        element={
          <div style={{ 
            textAlign: 'center', 
            padding: '2rem',
            color: '#666'
          }}>
            <h2>Page Not Found</h2>
            <p>The page you're looking for doesn't exist.</p>
          </div>
        } 
      />
    </Routes>
      </Suspense>
    </ErrorBoundary>
  );
}
