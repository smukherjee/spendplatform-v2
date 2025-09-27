import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.tsx';

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav style={{ 
      padding: '1rem', 
      background: '#f5f5f5', 
      borderBottom: '1px solid #ddd',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <div>
        <Link to="/dashboard">Dashboard</Link> |{' '}
        <Link to="/invoices">Invoices</Link> |{' '}
        <Link to="/suppliers">Suppliers</Link> |{' '}
        <Link to="/business-units">Business Units</Link> |{' '}
        <Link to="/regions">Regions</Link> |{' '}
        {user && (user.role === 'client_admin' || user.role === 'superadmin') && (
          <>
            <Link to="/roles">Roles</Link> |{' '}
            <Link to="/users">Users</Link> |{' '}
          </>
        )}
        {user && user.role === 'superadmin' && (
          <>
            <Link to="/clients">Clients</Link> |{' '}
          </>
        )}
        <Link to="/subcategories">Subcategories</Link> |{' '}
        <Link to="/unit-of-measure">Unit Of Measure</Link> |{' '}
        <Link to="/currency">Currency</Link> |{' '}
        <Link to="/import-errors">Import Errors</Link> |{' '}
        <Link to="/reporting">Reporting</Link> |{' '}
        {user && (user.role === 'client_admin' || user.role === 'superadmin') && (
          <>
            <Link to="/client-settings">Client Settings</Link> |{' '}
          </>
        )}
        <Link to="/settings">Settings</Link>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {user && (
          <span style={{ fontSize: '0.9rem', color: '#666' }}>
            Welcome, {user.username} ({user.role})
          </span>
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
            fontSize: '0.9rem'
          }}
        >
          Logout
        </button>
      </div>
    </nav>
  );
}
