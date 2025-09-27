import React from 'react';
import ErrorBoundary from './ErrorBoundary';
import { AppProvider } from './context/AppContext';
import NavBar from './components/NavBar';
import AppRoutes from './routes';

export default function App() {
  return (
    <AppProvider>
      <ErrorBoundary>
        <NavBar />
        <AppRoutes />
      </ErrorBoundary>
    </AppProvider>
  );
}
