import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';    
import ErrorBoundary from './ErrorBoundary';
import { AppProvider } from './context/AppContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import NavBar from './components/NavBar';
import AppRoutes from './routes';

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();
  
  // Don't show NavBar until auth is fully loaded
  const shouldShowNavBar = isAuthenticated && !isLoading;
  
  // Debug logging to track NavBar rendering
  console.log('🔍 App.tsx render state:', {
    isAuthenticated,
    isLoading,
    shouldShowNavBar
  });
  
  return (
    <>
      {shouldShowNavBar && (
        <>
          <div style={{ padding: '10px', background: '#e6ffe6', fontSize: '12px' }}>
            🟢 SYNC MODE: NavBar rendered after complete login process
          </div>
          <NavBar />
        </>
      )}
      <AppRoutes />
    </>
  );
}

export default function App() {
  return (
    <AppProvider>
      <ErrorBoundary>
        <Router>
          <AuthProvider>
            <AppContent />
          </AuthProvider>
        </Router>
      </ErrorBoundary>
    </AppProvider>
  );
}
