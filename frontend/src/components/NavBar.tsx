import React, { useMemo, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useMultiplePermissions } from '../services/permissions';

// Memoized navigation link component to prevent unnecessary re-renders
const NavLink = React.memo<{
  to: string;
  children: React.ReactNode;
  className?: string;
}>(({ to, children, className = '' }) => (
  <Link 
    to={to} 
    style={{ 
      marginRight: '1rem', 
      color: '#007bff', 
      textDecoration: 'none' 
    }}
    className={className}
  >
    {children}
  </Link>
));

NavLink.displayName = 'NavLink';

// Optimized NavBar with React.memo and proper memoization
const NavBar = React.memo(() => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Memoize screens array to prevent recreation on every render
  const screens = useMemo(() => [
    '/dashboard',
    '/invoices', 
    '/suppliers',
    '/business-units',
    '/regions',
    '/roles',
    '/users',
    '/clients',
    '/subcategories',
    '/unit-of-measure',
    '/currency',
    '/import-errors',
    '/reporting',
    '/client-settings',
    '/settings',
    '/screen-permissions'
  ], []);
  
  // Fix: Proper user key memoization with correct dependencies
  const userKey = useMemo(() => 
    user ? `${user.user_id}-${user.role}-${user.client_id}` : 'no-user', 
    [user] // Simplified dependency - user object change will trigger re-memo
  );
  
  const { permissions, loading } = useMultiplePermissions(screens, userKey);

  // Memoize logout handler to prevent recreation
  const handleLogout = useCallback(() => {
    logout();
    navigate('/login');
  }, [logout, navigate]);

  // Memoize access check function
  const hasAccess = useCallback((screen: string) => {
    // If permissions are still loading, show only essential navigation based on role
    if (loading) {
      // Always show dashboard - accessible to all authenticated users
      if (screen === '/dashboard') return true;
      
      // Show basic screens for all roles
      if (screen === '/invoices' || screen === '/suppliers') return true;
      
      // Show admin screens only for admin roles
      if (user?.role === 'superadmin') {
        return ['/clients', '/roles', '/users', '/screen-permissions', '/settings'].includes(screen);
      }
      
      if (user?.role === 'client_admin') {
        return ['/users', '/roles', '/client-settings', '/reporting'].includes(screen);
      }
      
      // For regular users, show limited access
      return false;
    }
    
    // Use actual permissions when loaded
    return permissions.get(screen) === true;
  }, [loading, permissions, user?.role]);

  return (
    <nav style={{ 
      padding: '1rem', 
      background: '#f5f5f5', 
      borderBottom: '1px solid #ddd',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.5rem' }}>
        {loading && (
          <span style={{ color: '#666', fontSize: '0.8rem', marginRight: '1rem' }}>
            Loading menu...
          </span>
        )}

        {/* Core Operations */}
        {hasAccess('/dashboard') && (
          <>
            <Link to="/dashboard" style={{ fontWeight: 'bold' }}>Dashboard</Link>
            <span style={{ color: '#ccc' }}>|</span>
          </>
        )}
        
        {hasAccess('/invoices') && (
          <>
            <Link to="/invoices">Invoices</Link>
            <span style={{ color: '#ccc' }}>|</span>
          </>
        )}
        
        {hasAccess('/suppliers') && (
          <>
            <Link to="/suppliers">Suppliers</Link>
            <span style={{ color: '#ccc' }}>|</span>
          </>
        )}

        {/* Organization & Structure */}
        {(hasAccess('/business-units') || hasAccess('/regions')) && (
          <>
            {hasAccess('/business-units') && (
              <>
                <Link to="/business-units">Business Units</Link>
                <span style={{ color: '#ccc' }}>|</span>
              </>
            )}
            
            {hasAccess('/regions') && (
              <>
                <Link to="/regions">Regions</Link>
                <span style={{ color: '#ccc' }}>|</span>
              </>
            )}
          </>
        )}

        {/* Master Data */}
        {(hasAccess('/subcategories') || hasAccess('/unit-of-measure') || hasAccess('/currency')) && (
          <>
            {hasAccess('/subcategories') && (
              <>
                <Link to="/subcategories">Categories</Link>
                <span style={{ color: '#ccc' }}>|</span>
              </>
            )}
            
            {hasAccess('/unit-of-measure') && (
              <>
                <Link to="/unit-of-measure">Units</Link>
                <span style={{ color: '#ccc' }}>|</span>
              </>
            )}
            
            {hasAccess('/currency') && (
              <>
                <Link to="/currency">Currency</Link>
                <span style={{ color: '#ccc' }}>|</span>
              </>
            )}
          </>
        )}

        {/* User & Access Management */}
        {(hasAccess('/users') || hasAccess('/roles') || hasAccess('/clients')) && (
          <>
            {hasAccess('/users') && (
              <>
                <Link to="/users">Users</Link>
                <span style={{ color: '#ccc' }}>|</span>
              </>
            )}
            
            {hasAccess('/roles') && (
              <>
                <Link to="/roles">Roles</Link>
                <span style={{ color: '#ccc' }}>|</span>
              </>
            )}
            
            {hasAccess('/clients') && (
              <>
                <Link to="/clients">Clients</Link>
                <span style={{ color: '#ccc' }}>|</span>
              </>
            )}
          </>
        )}

        {/* Reports & Analytics */}
        {hasAccess('/reporting') && (
          <>
            <Link to="/reporting">Reports</Link>
            <span style={{ color: '#ccc' }}>|</span>
          </>
        )}

        {/* System & Admin */}
        {(hasAccess('/import-errors') || hasAccess('/client-settings') || hasAccess('/settings') || hasAccess('/screen-permissions')) && (
          <>
            {hasAccess('/import-errors') && (
              <>
                <Link to="/import-errors">Import Errors</Link>
                <span style={{ color: '#ccc' }}>|</span>
              </>
            )}
            
            {hasAccess('/client-settings') && (
              <>
                <Link to="/client-settings">Client Settings</Link>
                <span style={{ color: '#ccc' }}>|</span>
              </>
            )}
            
            {hasAccess('/settings') && (
              <>
                <Link to="/settings">Settings</Link>
                <span style={{ color: '#ccc' }}>|</span>
              </>
            )}
            
            {hasAccess('/screen-permissions') && (
              <Link to="/screen-permissions">Permissions</Link>
            )}
          </>
        )}
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {user && (
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.9rem', color: '#333' }}>
              {user.username}
            </div>
            <div style={{ 
              fontSize: '0.75rem', 
              color: user.role === 'superadmin' ? '#e74c3c' : 
                     user.role === 'client_admin' ? '#f39c12' : '#2ecc71',
              fontWeight: 'bold'
            }}>
              {user.role.replace('_', ' ').toUpperCase()}
              {loading && ' (Loading...)'}
            </div>
          </div>
        )}
        <button 
          onClick={handleLogout}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '0.9rem',
            transition: 'background-color 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#c82333'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#dc3545'}
        >
          Logout
        </button>
      </div>
    </nav>
  );
});

NavBar.displayName = 'NavBar';

export default NavBar;
