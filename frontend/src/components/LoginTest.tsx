import React, { useState } from 'react';
import { createTestToken, logout } from '../services/api';

export default function LoginTest() {
  const [status, setStatus] = useState<string>('Not logged in');
  const [loading, setLoading] = useState(false);

  const handleTestLogin = async () => {
    setLoading(true);
    setStatus('Attempting login...');
    
    try {
      const success = await createTestToken();
      if (success) {
        setStatus('✅ Login successful! Token saved to localStorage');
      } else {
        setStatus('❌ Login failed');
      }
    } catch (error) {
      setStatus(`❌ Login error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    setStatus('Logged out');
  };

  const checkToken = () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setStatus(`✅ Token present: ${token.substring(0, 20)}...`);
    } else {
      setStatus('❌ No token found');
    }
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', margin: '20px', borderRadius: '8px' }}>
      <h3>Authentication Test</h3>
      <p>Status: {status}</p>
      
      <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
        <button 
          onClick={handleTestLogin} 
          disabled={loading}
          style={{ padding: '8px 16px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}
        >
          {loading ? 'Logging in...' : 'Test Login (user/userpw)'}
        </button>
        
        <button 
          onClick={handleLogout}
          style={{ padding: '8px 16px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px' }}
        >
          Logout
        </button>
        
        <button 
          onClick={checkToken}
          style={{ padding: '8px 16px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px' }}
        >
          Check Token
        </button>
      </div>
      
      <div style={{ marginTop: '15px', fontSize: '12px', color: '#666' }}>
        <p>Available test users in backend:</p>
        <ul>
          <li>superadmin / superadminpw (superadmin role)</li>
          <li>clientadmin / clientadminpw (client_admin role)</li>
          <li>user / userpw (user role) ← Currently used</li>
        </ul>
      </div>
    </div>
  );
}