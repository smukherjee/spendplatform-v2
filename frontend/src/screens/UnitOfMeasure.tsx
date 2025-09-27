import React, { useEffect, useState } from 'react';
import { fetchUnitOfMeasures, createUnitOfMeasure, deleteUnitOfMeasure } from '../services/apiEntities';

export default function UnitOfMeasure() {
  const [units, setUnits] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newUnit, setNewUnit] = useState<{ name: string }>({ name: '' });

  useEffect(() => {
    fetchUnitOfMeasures()
      .then((data) => setUnits(data as any[]))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createUnitOfMeasure(newUnit);
      setUnits((prev) => [...prev, created]);
      setNewUnit({ name: '' });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: string | number) => {
    try {
      await deleteUnitOfMeasure(id);
      setUnits((prev) => prev.filter((u) => u.id !== id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading units of measure...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Units of Measure</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Name"
          value={newUnit.name}
          onChange={(e) => setNewUnit({ name: e.target.value })}
          required
        />
        <button type="submit">Add</button>
      </form>
      <ul>
        {units.map((u) => (
          <li key={u.id}>
            {u.name}
            <button onClick={() => handleDelete(u.id)} style={{ marginLeft: '1rem' }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
