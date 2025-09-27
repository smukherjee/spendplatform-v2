import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';    
import ErrorBoundary from './ErrorBoundary.tsx';
import { AppProvider } from './context/AppContext.tsx';
import { AuthProvider, useAuth } from './contexts/AuthContext.tsx';
import NavBar from './components/NavBar.tsx';
import AppRoutes from './routes.tsx';

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
