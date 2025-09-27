import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';    
import ErrorBoundary from './ErrorBoundary';
import { AppProvider } from './context/AppContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import NavBar from './components/NavBar';
import AppRoutes from './routes';

function AppContent() {
  const { isAuthenticated } = useAuth();
  
  return (
    <>
      {isAuthenticated && <NavBar />}
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
