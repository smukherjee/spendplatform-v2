import React, { useEffect, useState } from 'react';
import { fetchSuppliers, createSupplier, deleteSupplier } from '../services/apiEntities.ts';

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newSupplier, setNewSupplier] = useState<{ name: string }>({ name: '' });

  useEffect(() => {
    fetchSuppliers()
      .then((data) => setSuppliers(data as any[]))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createSupplier(newSupplier);
      setSuppliers((prev) => [...prev, created]);
      setNewSupplier({ name: '' });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: string | number) => {
    try {
      await deleteSupplier(id);
      setSuppliers((prev) => prev.filter((s) => s.id !== id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading suppliers...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Suppliers</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Name"
          value={newSupplier.name}
          onChange={(e) => setNewSupplier({ name: e.target.value })}
          required
        />
        <button type="submit">Add</button>
      </form>
      <ul>
        {suppliers.map((s) => (
          <li key={s.id}>
            {s.name}
            <button onClick={() => handleDelete(s.id)} style={{ marginLeft: '1rem' }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
