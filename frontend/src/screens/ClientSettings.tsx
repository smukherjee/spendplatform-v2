import React, { useEffect, useState } from 'react';
import { fetchClientSettings, createClientSetting, deleteClientSetting } from '../services/apiEntities.ts';

export default function ClientSettings() {
  const [settings, setSettings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newSetting, setNewSetting] = useState<{ key: string; value: string }>({ key: '', value: '' });

  useEffect(() => {
    fetchClientSettings()
      .then((data) => setSettings(data as any[]))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createClientSetting(newSetting);
      setSettings((prev) => [...prev, created]);
      setNewSetting({ key: '', value: '' });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: string | number) => {
    try {
      await deleteClientSetting(id);
      setSettings((prev) => prev.filter((s) => s.id !== id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading client settings...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Client Settings</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Key"
          value={newSetting.key}
          onChange={(e) => setNewSetting({ ...newSetting, key: e.target.value })}
          required
        />
        <input
          type="text"
          placeholder="Value"
          value={newSetting.value}
          onChange={(e) => setNewSetting({ ...newSetting, value: e.target.value })}
          required
        />
        <button type="submit">Add</button>
      </form>
      <ul>
        {settings.map((s) => (
          <li key={s.id}>
            {s.key}: {s.value}
            <button onClick={() => handleDelete(s.id)} style={{ marginLeft: '1rem' }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
