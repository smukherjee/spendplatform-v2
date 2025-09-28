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
    if (loading) {
      // Fallback logic during loading
      if (screen === '/dashboard') return true;
      if (screen === '/invoices' || screen === '/suppliers') return true;
      
      if (user?.role === 'superadmin') {
        return ['/clients', '/roles', '/users', '/screen-permissions', '/settings'].includes(screen);
      }
      
      if (user?.role === 'client_admin') {
        return ['/users', '/roles', '/client-settings', '/reporting'].includes(screen);
      }
      
      return false;
    }
    
    return permissions.get(screen) === true;
  }, [loading, permissions, user?.role]);

  // Memoize navigation items to prevent recreation
  const navigationItems = useMemo(() => {
    const items = [
      { path: '/dashboard', label: 'Dashboard' },
      { path: '/invoices', label: 'Invoices' },
      { path: '/suppliers', label: 'Suppliers' },
      { path: '/business-units', label: 'Business Units' },
      { path: '/regions', label: 'Regions' },
      { path: '/roles', label: 'Roles' },
      { path: '/users', label: 'Users' },
      { path: '/clients', label: 'Clients' },
      { path: '/subcategories', label: 'Subcategories' },
      { path: '/unit-of-measure', label: 'Unit of Measure' },
      { path: '/currency', label: 'Currency' },
      { path: '/import-errors', label: 'Import Errors' },
      { path: '/reporting', label: 'Reporting' },
      { path: '/client-settings', label: 'Client Settings' },
      { path: '/settings', label: 'Settings' },
      { path: '/screen-permissions', label: 'Screen Permissions' }
    ];

    return items.filter(item => hasAccess(item.path));
  }, [hasAccess]);

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
        
        {navigationItems.map(({ path, label }) => (
          <NavLink key={path} to={path}>
            {label}
          </NavLink>
        ))}
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {user && (
          <span style={{ color: '#666', fontSize: '0.9rem' }}>
            {user.username} ({user.role})
          </span>
        )}
        <button
          onClick={handleLogout}
          style={{
            padding: '0.5rem 1rem',
            background: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Logout
        </button>
      </div>
    </nav>
  );
});

NavBar.displayName = 'NavBar';

export default NavBar;