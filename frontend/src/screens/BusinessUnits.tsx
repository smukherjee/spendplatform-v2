import React, { useEffect, useState } from 'react';
import { fetchBusinessUnits, createBusinessUnit, deleteBusinessUnit } from '../services/apiEntities.ts';

export default function BusinessUnits() {
  const [units, setUnits] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newUnit, setNewUnit] = useState<{ name: string; code: string }>({ name: '', code: '' });

  useEffect(() => {
    console.log('Fetching business units...');
    fetchBusinessUnits()
      .then((data) => {
        console.log('Fetched business units:', data);
        setUnits(data as any[]);
      })
      .catch((err) => {
        console.error('Error fetching business units:', err);
        setError(err.message);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createBusinessUnit(newUnit);
      setUnits((prev) => [...prev, created]);
      setNewUnit({ name: '', code: '' });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: string | number) => {
    try {
      await deleteBusinessUnit(id);
      setUnits((prev) => prev.filter((u) => u.id !== id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading business units...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Business Units</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Name"
          value={newUnit.name}
          onChange={(e) => setNewUnit({ ...newUnit, name: e.target.value })}
          required
        />
        <input
          type="text"
          placeholder="Code"
          value={newUnit.code}
          onChange={(e) => setNewUnit({ ...newUnit, code: e.target.value })}
          required
        />
        <button type="submit">Add</button>
      </form>
      {units.length === 0 && !loading ? (
        <div>No business units found.</div>
      ) : (
        <ul>
          {units.map((unit) => (
            <li key={unit.id}>
              {unit.name} ({unit.code})
              <button onClick={() => handleDelete(unit.id)} style={{ marginLeft: '1rem' }}>Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
