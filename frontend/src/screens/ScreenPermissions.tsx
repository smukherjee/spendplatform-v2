import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { invalidatePermissionCache } from '../services/permissions';

interface Screen {
  id: number;
  name: string;
  route: string;
  category: string;
  description: string;
  is_active: boolean;
}

interface Role {
  id: number;
  name: string;
}

interface RolePermission {
  id: number;
  role_id: number;
  screen_id: number;
  client_id: number;
  allow_access: boolean;
  screen: Screen;
  role_name: string;
}

export default function ScreenPermissions() {
  const [screens, setScreens] = useState<Screen[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<RolePermission[]>([]);
  const [selectedRole, setSelectedRole] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [screensRes, rolesRes, permissionsRes] = await Promise.all([
        api.get('/screen-permissions/screens'),
        api.get('/roles'),
        api.get('/screen-permissions/role-permissions')
      ]);
      
      setScreens(screensRes.data);
      setRoles(rolesRes.data);
      setPermissions(permissionsRes.data);
      
      if (rolesRes.data.length > 0) {
        setSelectedRole(rolesRes.data[0].id);
      }
    } catch (error) {
      console.error('Error loading data:', error);
      setMessage('Error loading data');
    } finally {
      setLoading(false);
    }
  };

  const handlePermissionToggle = (screenId: number, currentAccess: boolean) => {
    if (!selectedRole) return;

    const updatedPermissions = permissions.map(perm => {
      if (perm.role_id === selectedRole && perm.screen_id === screenId) {
        return { ...perm, allow_access: !currentAccess };
      }
      return perm;
    });

    // If permission doesn't exist, add it
    const existingPerm = permissions.find(p => p.role_id === selectedRole && p.screen_id === screenId);
    if (!existingPerm) {
      const screen = screens.find(s => s.id === screenId);
      const role = roles.find(r => r.id === selectedRole);
      if (screen && role) {
        updatedPermissions.push({
          id: Date.now(), // temporary ID
          role_id: selectedRole,
          screen_id: screenId,
          client_id: 1, // will be set by backend
          allow_access: !currentAccess,
          screen: screen,
          role_name: role.name
        });
      }
    }

    setPermissions(updatedPermissions);
  };

  const savePermissions = async () => {
    if (!selectedRole) return;

    try {
      setSaving(true);
      
      const rolePermissions = permissions
        .filter(p => p.role_id === selectedRole)
        .map(p => ({
          screen_id: p.screen_id,
          allow_access: p.allow_access
        }));

      await api.post('/screen-permissions/role-permissions/bulk', {
        role_id: selectedRole,
        client_id: 1, // will be determined by backend based on user
        permissions: rolePermissions
      });

      // Clear permission cache so changes are reflected immediately
      invalidatePermissionCache();

      setMessage('✅ Permissions saved successfully! Cache cleared - changes will be visible immediately.');
      setTimeout(() => setMessage(''), 5000);
    } catch (error) {
      console.error('Error saving permissions:', error);
      setMessage('❌ Error saving permissions');
    } finally {
      setSaving(false);
    }
  };

  const getPermissionForScreen = (screenId: number): boolean => {
    if (!selectedRole) return false;
    const permission = permissions.find(p => p.role_id === selectedRole && p.screen_id === screenId);
    return permission ? permission.allow_access : false;
  };

  const groupScreensByCategory = () => {
    const grouped: { [key: string]: Screen[] } = {};
    screens.forEach(screen => {
      const category = screen.category || 'Other';
      if (!grouped[category]) grouped[category] = [];
      grouped[category].push(screen);
    });
    return grouped;
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '400px',
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }}>
        <div>Loading screen permissions...</div>
      </div>
    );
  }

  const groupedScreens = groupScreensByCategory();

  return (
    <div style={{ 
      padding: '2rem', 
      fontFamily: 'system-ui, -apple-system, sans-serif',
      maxWidth: '1200px',
      margin: '0 auto'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '2rem',
        borderBottom: '2px solid #e5e7eb',
        paddingBottom: '1rem'
      }}>
        <h1 style={{ margin: 0, color: '#1f2937' }}>Screen Permissions Management</h1>
        <button
          onClick={savePermissions}
          disabled={saving || !selectedRole}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: saving ? '#9ca3af' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: saving ? 'not-allowed' : 'pointer',
            fontWeight: '500'
          }}
        >
          {saving ? 'Saving...' : 'Save Permissions'}
        </button>
      </div>

      {message && (
        <div style={{
          padding: '1rem',
          backgroundColor: message.includes('✅') ? '#d1fae5' : '#fee2e2',
          color: message.includes('✅') ? '#047857' : '#dc2626',
          borderRadius: '0.5rem',
          marginBottom: '1rem'
        }}>
          {message}
        </div>
      )}

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '300px 1fr', 
        gap: '2rem',
        alignItems: 'start'
      }}>
        {/* Role Selection */}
        <div style={{
          backgroundColor: '#f9fafb',
          padding: '1.5rem',
          borderRadius: '0.5rem',
          border: '1px solid #e5e7eb'
        }}>
          <h3 style={{ marginTop: 0, color: '#374151' }}>Select Role</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {roles.map(role => (
              <button
                key={role.id}
                onClick={() => setSelectedRole(role.id)}
                style={{
                  padding: '0.75rem',
                  backgroundColor: selectedRole === role.id ? '#3b82f6' : 'white',
                  color: selectedRole === role.id ? 'white' : '#374151',
                  border: '1px solid #d1d5db',
                  borderRadius: '0.375rem',
                  cursor: 'pointer',
                  textAlign: 'left',
                  fontWeight: selectedRole === role.id ? '500' : 'normal'
                }}
              >
                {role.name}
              </button>
            ))}
          </div>
        </div>

        {/* Permissions Grid */}
        <div>
          {selectedRole && (
            <>
              <h3 style={{ marginTop: 0, color: '#374151' }}>
                Permissions for: {roles.find(r => r.id === selectedRole)?.name}
              </h3>
              
              {Object.entries(groupedScreens).map(([category, categoryScreens]) => (
                <div key={category} style={{ marginBottom: '2rem' }}>
                  <h4 style={{ 
                    color: '#6b7280', 
                    fontSize: '1.1rem',
                    marginBottom: '1rem',
                    borderBottom: '1px solid #e5e7eb',
                    paddingBottom: '0.5rem'
                  }}>
                    {category}
                  </h4>
                  
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                    gap: '1rem'
                  }}>
                    {categoryScreens.map(screen => {
                      const hasAccess = getPermissionForScreen(screen.id);
                      return (
                        <div
                          key={screen.id}
                          style={{
                            backgroundColor: 'white',
                            border: `2px solid ${hasAccess ? '#10b981' : '#e5e7eb'}`,
                            borderRadius: '0.5rem',
                            padding: '1rem',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                          }}
                          onClick={() => handlePermissionToggle(screen.id, hasAccess)}
                        >
                          <div style={{ 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            alignItems: 'center',
                            marginBottom: '0.5rem'
                          }}>
                            <h5 style={{ margin: 0, color: '#1f2937' }}>{screen.name}</h5>
                            <div style={{
                              width: '20px',
                              height: '20px',
                              borderRadius: '50%',
                              backgroundColor: hasAccess ? '#10b981' : '#ef4444',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: 'white',
                              fontSize: '12px',
                              fontWeight: 'bold'
                            }}>
                              {hasAccess ? '✓' : '✗'}
                            </div>
                          </div>
                          <div style={{ 
                            fontSize: '0.8rem', 
                            color: '#6b7280',
                            marginBottom: '0.5rem'
                          }}>
                            {screen.route}
                          </div>
                          {screen.description && (
                            <div style={{ 
                              fontSize: '0.85rem', 
                              color: '#4b5563'
                            }}>
                              {screen.description}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}