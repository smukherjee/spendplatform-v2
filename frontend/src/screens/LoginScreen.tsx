import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login as apiLogin } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface LoginScreenProps {
  onLoginSuccess?: (userData: any) => void;
}

export default function LoginScreen({ onLoginSuccess }: LoginScreenProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [debugLogs, setDebugLogs] = useState<string[]>([]);
  const navigate = useNavigate();
  const { login: authLogin } = useAuth();

  const addDebugLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    const logMessage = `[${timestamp}] ${message}`;
    console.log(logMessage);
    setDebugLogs(prev => [...prev.slice(-4), logMessage]); // Keep last 5 logs
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    addDebugLog(`🔄 Starting login attempt for user: ${username}`);

    try {
      addDebugLog(`📡 Calling API login...`);
      const result = await apiLogin(username, password);
      addDebugLog(`✅ API login successful: ${JSON.stringify(result.user)}`);
      
      // Call AuthContext login to update app state - WAIT for completion
      if (result.user) {
        addDebugLog(`🔐 Updating auth context and waiting for completion...`);
        await authLogin(result.user);
        addDebugLog(`✅ Auth context updated - NavBar can now render safely`);
      }
      
      if (onLoginSuccess && result.user) {
        addDebugLog(`📞 Calling onLoginSuccess callback...`);
        onLoginSuccess(result.user);
      }
      
      addDebugLog(`🏠 Navigating to dashboard...`);
      // Redirect to dashboard after successful login
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Login failed:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Login failed. Please check your credentials.';
      addDebugLog(`❌ Login failed: ${errorMessage}`);
      addDebugLog(`🔍 Error details: ${JSON.stringify(err.response?.data || err)}`);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleTestUserLogin = async (testUsername: string, testPassword: string) => {
    setUsername(testUsername);
    setPassword(testPassword);
    setLoading(true);
    setError('');
    addDebugLog(`🧪 Test login attempt: ${testUsername}/${testPassword}`);

    try {
      addDebugLog(`📡 Calling API login for test user...`);
      const result = await apiLogin(testUsername, testPassword);
      addDebugLog(`✅ Test login successful: ${JSON.stringify(result.user)}`);
      
      // Call AuthContext login to update app state - WAIT for completion
      if (result.user) {
        addDebugLog(`🔐 Updating auth context for test user and waiting...`);
        await authLogin(result.user);
        addDebugLog(`✅ Test user auth context updated - NavBar ready`);
      }
      
      if (onLoginSuccess && result.user) {
        addDebugLog(`📞 Calling onLoginSuccess callback for test user...`);
        onLoginSuccess(result.user);
      }
      
      addDebugLog(`🏠 Navigating to dashboard from test login...`);
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Test login failed:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Login failed. Please check your credentials.';
      addDebugLog(`❌ Test login failed: ${errorMessage}`);
      addDebugLog(`🔍 Test error details: ${JSON.stringify(err.response?.data || err)}`);
      setError(errorMessage);
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
              onClick={() => handleTestUserLogin('user', 'user123')}
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
              Login as User (user/user123)
            </button>
            
            <button
              type="button"
              onClick={() => handleTestUserLogin('clientadmin', 'admin123')}
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
              Login as Client Admin (clientadmin/admin123)
            </button>
            
            <button
              type="button"
              onClick={() => handleTestUserLogin('superadmin', 'superadmin123')}
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
              Login as Super Admin (superadmin/superadmin123)
            </button>
          </div>
        </div>

        {/* Debug Logs Section */}
        {debugLogs.length > 0 && (
          <div style={{
            marginTop: '1rem',
            borderTop: '1px solid #eee',
            paddingTop: '1rem'
          }}>
            <p style={{ fontSize: '0.8rem', color: '#666', marginBottom: '0.5rem', textAlign: 'center' }}>
              🐛 Debug Logs (Development Mode):
            </p>
            <div style={{
              backgroundColor: '#f8f9fa',
              border: '1px solid #e9ecef',
              borderRadius: '4px',
              padding: '0.5rem',
              fontSize: '0.7rem',
              fontFamily: 'monospace',
              maxHeight: '150px',
              overflowY: 'auto'
            }}>
              {debugLogs.map((log, index) => (
                <div key={index} style={{ marginBottom: '0.25rem', lineHeight: 1.3 }}>
                  {log}
                </div>
              ))}
            </div>
            <button
              type="button"
              onClick={() => setDebugLogs([])}
              style={{
                marginTop: '0.5rem',
                padding: '0.25rem 0.5rem',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                fontSize: '0.7rem',
                cursor: 'pointer',
                width: '100%'
              }}
            >
              Clear Debug Logs
            </button>
          </div>
        )}
      </div>
    </div>
  );
}