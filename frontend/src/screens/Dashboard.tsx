import React from 'react';
import { useAuth } from '../contexts/AuthContext.tsx';

export default function Dashboard() {
  const { user } = useAuth();

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      <h1>Dashboard</h1>
      {user && (
        <div style={{ 
          background: '#f8f9fa', 
          border: '1px solid #dee2e6', 
          borderRadius: '8px', 
          padding: '1rem', 
          marginBottom: '2rem' 
        }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>Welcome back!</h3>
          <p style={{ margin: '0', color: '#6c757d' }}>
            Logged in as: <strong>{user.username}</strong> ({user.role})
            <br />
            Client ID: {user.client_id}
          </p>
        </div>
      )}
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
        <div style={{ 
          background: 'white', 
          border: '1px solid #dee2e6', 
          borderRadius: '8px', 
          padding: '1rem' 
        }}>
          <h4 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>Quick Actions</h4>
          <p style={{ margin: '0', color: '#6c757d', fontSize: '0.9rem' }}>
            Use the navigation bar above to access different sections of the application.
          </p>
        </div>
        
        <div style={{ 
          background: 'white', 
          border: '1px solid #dee2e6', 
          borderRadius: '8px', 
          padding: '1rem' 
        }}>
          <h4 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>System Status</h4>
          <p style={{ margin: '0', color: '#28a745', fontSize: '0.9rem' }}>
            ✅ Authentication: Active
            <br />
            ✅ Database: Connected
            <br />
            ✅ API: Available
          </p>
        </div>
      </div>
    </div>
  );
}
