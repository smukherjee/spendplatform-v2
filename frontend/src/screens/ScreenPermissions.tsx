import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../services/api';
import { invalidatePermissionCache } from '../services/permissions';

interface Role {
  id: number;
  name: string;
}

type ActionPermissionField = 'can_view' | 'can_create' | 'can_edit' | 'can_delete' | 'can_export' | 'can_import';
type PermissionField = ActionPermissionField | 'allow_full_access' | 'deny_access';

interface RolePermissionScreen {
  screen_id: number;
  screen_name: string;
  screen_route: string;
  category: string | null;
  screen_description?: string | null;
  is_active?: boolean;
  can_view: boolean;
  can_create: boolean;
  can_edit: boolean;
  can_delete: boolean;
  can_export: boolean;
  can_import: boolean;
  allow_full_access: boolean;
  deny_access: boolean;
}

interface RolePermissionsMatrix {
  role_id: number;
  role_name: string;
  client_id: number | null;
  screens: RolePermissionScreen[];
}

const ACTION_FIELDS: ActionPermissionField[] = [
  'can_view',
  'can_create',
  'can_edit',
  'can_delete',
  'can_export',
  'can_import'
];

const ACTION_LABELS: Record<ActionPermissionField, string> = {
  can_view: 'View',
  can_create: 'Create',
  can_edit: 'Edit',
  can_delete: 'Delete',
  can_export: 'Export',
  can_import: 'Import'
};

const SPECIAL_LABELS: Record<Exclude<PermissionField, ActionPermissionField>, string> = {
  allow_full_access: 'Full Access',
  deny_access: 'Deny Access'
};

const DEFAULT_CLIENT_ID = 1;

export default function ScreenPermissions() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [selectedRole, setSelectedRole] = useState<number | null>(null);
  const [permissionsMatrix, setPermissionsMatrix] = useState<RolePermissionsMatrix | null>(null);
  const [loading, setLoading] = useState(true);
  const [matrixLoading, setMatrixLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [hasChanges, setHasChanges] = useState(false);
  const [activeClientId, setActiveClientId] = useState<number | null>(DEFAULT_CLIENT_ID);

  const fetchRolePermissions = useCallback(
    async (roleId: number, clientIdOverride?: number | null) => {
      try {
        setMatrixLoading(true);
        setMessage('');

        const effectiveClientId = clientIdOverride ?? activeClientId ?? undefined;
        const config =
          effectiveClientId !== undefined
            ? { params: { client_id: effectiveClientId } }
            : undefined;

        const response = await api.get(`/screen-permissions/roles/${roleId}/permissions`, config);
        const matrix: RolePermissionsMatrix = response.data;

        setPermissionsMatrix(matrix);
        setActiveClientId(prev => {
          const nextClientId = matrix.client_id ?? (effectiveClientId ?? null);
          return prev === nextClientId ? prev : nextClientId;
        });
        setHasChanges(false);
      } catch (error) {
        console.error('Error fetching role permissions:', error);
        setMessage('Error fetching role permissions');
      } finally {
        setMatrixLoading(false);
      }
    },
    [activeClientId]
  );

  const loadInitialData = useCallback(async () => {
    try {
      setLoading(true);
      setMessage('');
      const rolesRes = await api.get('/roles');
      const roleList: Role[] = rolesRes.data || [];
      setRoles(roleList);

      const defaultRoleId = roleList.length > 0 ? roleList[0].id : null;
      if (defaultRoleId) {
        setSelectedRole(defaultRoleId);
        await fetchRolePermissions(defaultRoleId, DEFAULT_CLIENT_ID);
      } else {
        setPermissionsMatrix(null);
      }
    } catch (error) {
      console.error('Error loading roles:', error);
      setMessage('Error loading roles');
    } finally {
      setLoading(false);
    }
  }, [fetchRolePermissions]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  const handleRoleSelection = (roleId: number) => {
    if (roleId === selectedRole) return;
    setSelectedRole(roleId);
    fetchRolePermissions(roleId);
  };

  const togglePermission = (screenId: number, field: PermissionField) => {
    setPermissionsMatrix(prev => {
      if (!prev) return prev;
      setHasChanges(true);

      const updatedScreens = prev.screens.map(screen => {
        if (screen.screen_id !== screenId) return screen;

        const updated: RolePermissionScreen = { ...screen };
        const nextValue = !Boolean(screen[field as keyof RolePermissionScreen]);

        if (field === 'allow_full_access') {
          updated.allow_full_access = nextValue;
          if (nextValue) {
            ACTION_FIELDS.forEach(action => {
              updated[action] = true;
            });
            updated.deny_access = false;
          }
        } else if (field === 'deny_access') {
          updated.deny_access = nextValue;
          if (nextValue) {
            updated.allow_full_access = false;
            ACTION_FIELDS.forEach(action => {
              updated[action] = false;
            });
          }
        } else {
          const actionField = field as ActionPermissionField;
          updated[actionField] = nextValue;

          if (nextValue) {
            updated.deny_access = false;
          } else {
            updated.allow_full_access = false;
          }
        }

        return updated;
      });

      return { ...prev, screens: updatedScreens };
    });
  };

  const savePermissions = async () => {
    if (!selectedRole || !permissionsMatrix) {
      return;
    }

    try {
      setSaving(true);
      setMessage('');

      const payload = {
        client_id: activeClientId,
        screens: permissionsMatrix.screens.map(screen => ({
          screen_id: screen.screen_id,
          can_view: screen.can_view,
          can_create: screen.can_create,
          can_edit: screen.can_edit,
          can_delete: screen.can_delete,
          can_export: screen.can_export,
          can_import: screen.can_import,
          allow_full_access: screen.allow_full_access,
          deny_access: screen.deny_access
        }))
      };

      await api.put(`/screen-permissions/roles/${selectedRole}/permissions`, payload);
      invalidatePermissionCache();
      setMessage('✅ Permissions saved successfully');
      setHasChanges(false);

      await fetchRolePermissions(selectedRole);
    } catch (error) {
      console.error('Error saving permissions:', error);
      setMessage('Error saving permissions');
    } finally {
      setSaving(false);
    }
  };

  const groupedScreens = useMemo(() => {
    const grouped: Record<string, RolePermissionScreen[]> = {};

    permissionsMatrix?.screens.forEach(screen => {
      const categoryKey = screen.category ?? 'Other';
      if (!grouped[categoryKey]) {
        grouped[categoryKey] = [];
      }
      grouped[categoryKey].push(screen);
    });

    Object.keys(grouped).forEach(category => {
      grouped[category] = grouped[category].sort((a, b) => a.screen_name.localeCompare(b.screen_name));
    });

    return grouped;
  }, [permissionsMatrix]);

  if (loading) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '400px',
          fontFamily: 'system-ui, -apple-system, sans-serif'
        }}
      >
        <div>Loading screen permissions...</div>
      </div>
    );
  }

  return (
    <div
      style={{
        padding: '2rem',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        maxWidth: '1300px',
        margin: '0 auto'
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem',
          borderBottom: '2px solid #e5e7eb',
          paddingBottom: '1rem'
        }}
      >
        <div>
          <h1 style={{ margin: 0, color: '#1f2937' }}>Screen Permissions Management</h1>
          {permissionsMatrix && (
            <div style={{ marginTop: '0.5rem', color: '#6b7280', fontSize: '0.9rem' }}>
              Role: <strong>{permissionsMatrix.role_name}</strong>
              {activeClientId !== null && ` · Client ID: ${activeClientId}`}
            </div>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {hasChanges && !saving && (
            <span style={{ color: '#d97706', fontWeight: 500 }}>Unsaved changes</span>
          )}
          <button
            onClick={savePermissions}
            disabled={saving || !selectedRole || !permissionsMatrix || !hasChanges}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: saving || !hasChanges ? '#9ca3af' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '0.5rem',
              cursor: saving || !hasChanges ? 'not-allowed' : 'pointer',
              fontWeight: 500
            }}
          >
            {saving ? 'Saving...' : 'Save Permissions'}
          </button>
        </div>
      </div>

      {message && (
        <div
          style={{
            padding: '1rem',
            backgroundColor: message.includes('✅') ? '#d1fae5' : '#fee2e2',
            color: message.includes('✅') ? '#047857' : '#dc2626',
            borderRadius: '0.5rem',
            marginBottom: '1rem'
          }}
        >
          {message}
        </div>
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '320px 1fr',
          gap: '2rem',
          alignItems: 'start'
        }}
      >
        <div
          style={{
            backgroundColor: '#f9fafb',
            padding: '1.5rem',
            borderRadius: '0.75rem',
            border: '1px solid #e5e7eb',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)'
          }}
        >
          <h3 style={{ marginTop: 0, color: '#374151' }}>Select Role</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '1rem' }}>
            {roles.map(role => (
              <button
                key={role.id}
                onClick={() => handleRoleSelection(role.id)}
                style={{
                  padding: '0.75rem',
                  backgroundColor: selectedRole === role.id ? '#3b82f6' : 'white',
                  color: selectedRole === role.id ? 'white' : '#374151',
                  border: '1px solid #d1d5db',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  textAlign: 'left',
                  fontWeight: selectedRole === role.id ? 600 : 400,
                  transition: 'all 0.2s'
                }}
              >
                {role.name}
              </button>
            ))}
          </div>
        </div>

        <div>
          {!selectedRole && (
            <div style={{ color: '#6b7280' }}>Select a role to view permissions.</div>
          )}

          {selectedRole && matrixLoading && (
            <div
              style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                minHeight: '200px',
                color: '#6b7280'
              }}
            >
              Refreshing permissions...
            </div>
          )}

          {selectedRole && !matrixLoading && permissionsMatrix && (
            <>
              {Object.keys(groupedScreens).length === 0 && (
                <div style={{ color: '#6b7280' }}>No screens available for this role.</div>
              )}

              {Object.entries(groupedScreens).map(([category, categoryScreens]) => (
                <div key={category} style={{ marginBottom: '2rem' }}>
                  <h4
                    style={{
                      color: '#6b7280',
                      fontSize: '1.1rem',
                      marginBottom: '1rem',
                      borderBottom: '1px solid #e5e7eb',
                      paddingBottom: '0.5rem'
                    }}
                  >
                    {category}
                  </h4>

                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
                      gap: '1rem'
                    }}
                  >
                    {categoryScreens.map(screen => {
                      const borderColor = screen.deny_access
                        ? '#dc2626'
                        : screen.allow_full_access
                        ? '#10b981'
                        : screen.can_view
                        ? '#3b82f6'
                        : '#e5e7eb';

                      return (
                        <div
                          key={screen.screen_id}
                          style={{
                            backgroundColor: 'white',
                            border: `2px solid ${borderColor}`,
                            borderRadius: '0.75rem',
                            padding: '1rem',
                            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
                          }}
                        >
                          <div
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              marginBottom: '0.75rem'
                            }}
                          >
                            <div>
                              <h5 style={{ margin: 0, color: '#1f2937' }}>{screen.screen_name}</h5>
                              <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>{screen.screen_route}</div>
                            </div>
                            <div
                              style={{
                                padding: '0.25rem 0.5rem',
                                borderRadius: '999px',
                                fontSize: '0.75rem',
                                fontWeight: 600,
                                backgroundColor: screen.deny_access
                                  ? '#fee2e2'
                                  : screen.allow_full_access
                                  ? '#d1fae5'
                                  : screen.can_view
                                  ? '#dbeafe'
                                  : '#f3f4f6',
                                color: screen.deny_access
                                  ? '#b91c1c'
                                  : screen.allow_full_access
                                  ? '#047857'
                                  : screen.can_view
                                  ? '#1d4ed8'
                                  : '#4b5563'
                              }}
                            >
                              {screen.deny_access
                                ? 'Denied'
                                : screen.allow_full_access
                                ? 'Full Access'
                                : screen.can_view
                                ? 'View'
                                : 'No Access'}
                            </div>
                          </div>

                          {screen.screen_description && (
                            <div style={{ fontSize: '0.85rem', color: '#4b5563', marginBottom: '1rem' }}>
                              {screen.screen_description}
                            </div>
                          )}

                          <div
                            style={{
                              display: 'flex',
                              flexDirection: 'column',
                              gap: '0.75rem'
                            }}
                          >
                            <div
                              style={{
                                display: 'flex',
                                flexWrap: 'wrap',
                                gap: '0.75rem'
                              }}
                            >
                              {ACTION_FIELDS.map(action => (
                                <label
                                  key={`${screen.screen_id}-${action}`}
                                  style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.4rem',
                                    fontSize: '0.85rem',
                                    color: '#374151',
                                    cursor: 'pointer'
                                  }}
                                >
                                  <input
                                    type="checkbox"
                                    checked={screen[action]}
                                    onChange={() => togglePermission(screen.screen_id, action)}
                                  />
                                  {ACTION_LABELS[action]}
                                </label>
                              ))}
                            </div>

                            <div
                              style={{
                                display: 'flex',
                                gap: '1rem',
                                flexWrap: 'wrap'
                              }}
                            >
                              {(Object.keys(SPECIAL_LABELS) as Array<PermissionField>).map(field => (
                                <label
                                  key={`${screen.screen_id}-${field}`}
                                  style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.4rem',
                                    fontSize: '0.85rem',
                                    color: field === 'deny_access' ? '#b91c1c' : '#047857',
                                    cursor: 'pointer'
                                  }}
                                >
                                  <input
                                    type="checkbox"
                                    checked={screen[field as keyof RolePermissionScreen] as boolean}
                                    onChange={() => togglePermission(screen.screen_id, field)}
                                  />
                                  {SPECIAL_LABELS[field as keyof typeof SPECIAL_LABELS]}
                                </label>
                              ))}
                            </div>
                          </div>
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