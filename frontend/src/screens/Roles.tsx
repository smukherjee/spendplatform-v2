import React, { useEffect, useState } from 'react';
import { fetchRoles, createRole, deleteRole } from '../services/apiEntities.ts';

export default function Roles() {
  const [roles, setRoles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newRole, setNewRole] = useState<{ name: string }>({ name: '' });

  useEffect(() => {
    fetchRoles()
      .then((data) => setRoles(data as any[]))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createRole(newRole);
      setRoles((prev) => [...prev, created]);
      setNewRole({ name: '' });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: string | number) => {
    try {
      await deleteRole(id);
      setRoles((prev) => prev.filter((r) => r.id !== id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading roles...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Roles</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Name"
          value={newRole.name}
          onChange={(e) => setNewRole({ name: e.target.value })}
          required
        />
        <button type="submit">Add</button>
      </form>
      <ul>
        {roles.map((r) => (
          <li key={r.id}>
            {r.name}
            <button onClick={() => handleDelete(r.id)} style={{ marginLeft: '1rem' }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
