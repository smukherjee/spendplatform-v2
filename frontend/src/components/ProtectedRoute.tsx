import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { usePermission } from '../services/permissions';

interface ProtectedRouteProps {
  children: any;
  requiredRoles?: string[]; // Keep for backward compatibility
  screenRoute?: string; // New screen-based permission
}

export default function ProtectedRoute({ children, requiredRoles = [], screenRoute }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();
  
  // Use screen-based permission if provided, otherwise fall back to current route
  const routeToCheck = screenRoute || location.pathname;
  const { hasAccess, loading: isCheckingPermission } = usePermission(routeToCheck);

  // Show loading while checking authentication or permissions
  if (isLoading || isCheckingPermission) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '4px solid #f3f3f3',
            borderTop: '4px solid #007bff',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }}></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check screen-based permissions first (preferred method)
  if (hasAccess === false) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        textAlign: 'center',
        padding: '2rem'
      }}>
        <div>
          <h2 style={{ color: '#dc3545', marginBottom: '1rem' }}>Access Denied</h2>
          <p style={{ color: '#666', marginBottom: '1.5rem' }}>
            You don't have permission to access this screen.
          </p>
          <p style={{ fontSize: '0.9rem', color: '#999' }}>
            Screen: {routeToCheck}
            <br />
            Your role: {user?.role}
          </p>
          <button
            onClick={() => window.history.back()}
            style={{
              marginTop: '1rem',
              padding: '0.5rem 1rem',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Fallback to role-based access for backward compatibility
  if (requiredRoles.length > 0 && hasAccess === null && user) {
    const hasRequiredRole = requiredRoles.includes(user.role);
    if (!hasRequiredRole) {
      return (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          fontFamily: 'system-ui, -apple-system, sans-serif',
          textAlign: 'center',
          padding: '2rem'
        }}>
          <div>
            <h2 style={{ color: '#dc3545', marginBottom: '1rem' }}>Access Denied</h2>
            <p style={{ color: '#666', marginBottom: '1.5rem' }}>
              You don't have permission to access this page.
            </p>
            <p style={{ fontSize: '0.9rem', color: '#999' }}>
              Required roles: {requiredRoles.join(', ')}
              <br />
              Your role: {user.role}
            </p>
            <button
              onClick={() => window.history.back()}
              style={{
                marginTop: '1rem',
                padding: '0.5rem 1rem',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Go Back
            </button>
          </div>
        </div>
      );
    }
  }

  // Render the protected component
  return children;
}