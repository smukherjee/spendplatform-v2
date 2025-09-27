import React, { useEffect, useState } from 'react';
import { fetchRegions, createRegion, deleteRegion } from '../services/apiEntities.ts';

export default function Regions() {
  const [regions, setRegions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newRegion, setNewRegion] = useState<{ name: string; code: string }>({ name: '', code: '' });

  useEffect(() => {
    fetchRegions()
      .then((data) => setRegions(data as any[]))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createRegion(newRegion);
      setRegions((prev) => [...prev, created]);
      setNewRegion({ name: '', code: '' });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: string | number) => {
    try {
      await deleteRegion(id);
      setRegions((prev) => prev.filter((r) => r.id !== id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading regions...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Regions</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Name"
          value={newRegion.name}
          onChange={(e) => setNewRegion({ ...newRegion, name: e.target.value })}
          required
        />
        <input
          type="text"
          placeholder="Code"
          value={newRegion.code}
          onChange={(e) => setNewRegion({ ...newRegion, code: e.target.value })}
          required
        />
        <button type="submit">Add</button>
      </form>
      <ul>
        {regions.map((r) => (
          <li key={r.id}>
            {r.name} ({r.code})
            <button onClick={() => handleDelete(r.id)} style={{ marginLeft: '1rem' }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
