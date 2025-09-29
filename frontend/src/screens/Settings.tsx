import React, { useEffect, useState } from 'react';
import { fetchSettings } from '../services/apiEntities';

export default function Settings() {
  const [settings, setSettings] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSettings()
      .then((data) => {
        // Backend returns an object, not an array
        if (data && typeof data === 'object') {
          setSettings(data);
        } else {
          console.warn('Settings API returned invalid data:', data);
          setError('Invalid data format received from server');
        }
      })
      .catch((err) => {
        console.error('Settings fetch error:', err);
        setError(err.response?.data?.detail || err.message || 'Failed to fetch settings');
      })
      .finally(() => setLoading(false));
  }, []);

  // Recursive function to render nested settings
  const renderSettingsObject = (obj: any, path: string = ''): React.ReactElement[] => {
    return Object.entries(obj).map(([key, value]) => {
      const fullPath = path ? `${path}.${key}` : key;
      
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        return (
          <div key={fullPath} style={{ marginLeft: path ? '20px' : '0', marginBottom: '10px' }}>
            <strong>{key}:</strong>
            <div style={{ marginLeft: '10px' }}>
              {renderSettingsObject(value, fullPath)}
            </div>
          </div>
        );
      } else {
        return (
          <div key={fullPath} style={{ marginLeft: path ? '20px' : '0', marginBottom: '5px' }}>
            <span style={{ fontWeight: 'bold' }}>{key}:</span> {JSON.stringify(value)}
          </div>
        );
      }
    });
  };

  if (loading) return <div>Loading settings...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h2>Application Settings</h2>
      <div style={{ 
        backgroundColor: '#f5f5f5', 
        padding: '20px', 
        borderRadius: '8px',
        fontFamily: 'monospace',
        lineHeight: '1.5'
      }}>
        {Object.keys(settings).length > 0 ? (
          renderSettingsObject(settings)
        ) : (
          <div>No settings available</div>
        )}
      </div>
      <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
        <p>📝 Settings are managed by system configuration and user roles.</p>
        <p>🔧 Contact your administrator to modify system settings.</p>
      </div>
    </div>
  );
}
