import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login as apiLogin } from '../services/api.ts';

interface LoginScreenProps {
  onLoginSuccess?: (userData: any) => void;
}

export default function LoginScreen({ onLoginSuccess }: LoginScreenProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await apiLogin(username, password);
      console.log('Login successful, redirecting...');
      
      if (onLoginSuccess && result.user) {
        onLoginSuccess(result.user);
      }
      
      // Redirect to dashboard after successful login
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Login failed:', err);
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleTestUserLogin = async (testUsername: string, testPassword: string) => {
    setUsername(testUsername);
    setPassword(testPassword);
    setLoading(true);
    setError('');

    try {
      const result = await apiLogin(testUsername, testPassword);
      console.log('Test login successful, redirecting...');
      
      if (onLoginSuccess && result.user) {
        onLoginSuccess(result.user);
      }
      
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Test login failed:', err);
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#f5f5f5',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{
        background: 'white',
        padding: '2rem',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        width: '100%',
        maxWidth: '400px'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ color: '#333', marginBottom: '0.5rem' }}>SpendPlatform v2</h1>
          <p style={{ color: '#666', margin: 0 }}>Enterprise Invoice & PO Management</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#333' }}>
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e: any) => setUsername(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '1rem',
                boxSizing: 'border-box'
              }}
              placeholder="Enter your username"
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#333' }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e: any) => setPassword(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '1rem',
                boxSizing: 'border-box'
              }}
              placeholder="Enter your password"
            />
          </div>

          {error && (
            <div style={{
              background: '#fee',
              color: '#c33',
              padding: '0.75rem',
              borderRadius: '4px',
              marginBottom: '1rem',
              fontSize: '0.9rem'
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: loading ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '1rem',
              fontWeight: '500',
              cursor: loading ? 'not-allowed' : 'pointer',
              marginBottom: '1rem'
            }}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* Test Users Section */}
        <div style={{
          borderTop: '1px solid #eee',
          paddingTop: '1rem',
          marginTop: '1rem'
        }}>
          <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '1rem', textAlign: 'center' }}>
            Development Test Users:
          </p>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <button
              type="button"
              onClick={() => handleTestUserLogin('user', 'userpw')}
              disabled={loading}
              style={{
                padding: '0.5rem',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '0.8rem',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              Login as User (user/userpw)
            </button>
            
            <button
              type="button"
              onClick={() => handleTestUserLogin('clientadmin', 'clientadminpw')}
              disabled={loading}
              style={{
                padding: '0.5rem',
                backgroundColor: '#ffc107',
                color: '#333',
                border: 'none',
                borderRadius: '4px',
                fontSize: '0.8rem',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              Login as Client Admin (clientadmin/clientadminpw)
            </button>
            
            <button
              type="button"
              onClick={() => handleTestUserLogin('superadmin', 'superadminpw')}
              disabled={loading}
              style={{
                padding: '0.5rem',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',  
                fontSize: '0.8rem',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              Login as Super Admin (superadmin/superadminpw)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}