import React, { useEffect, useState } from 'react';
import { fetchSubcategories, createSubcategory, deleteSubcategory } from '../services/apiEntities';

export default function Subcategories() {
  const [subcategories, setSubcategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newSubcategory, setNewSubcategory] = useState<{ name: string }>({ name: '' });

  useEffect(() => {
    fetchSubcategories()
      .then((data) => setSubcategories(data as any[]))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createSubcategory(newSubcategory);
      setSubcategories((prev) => [...prev, created]);
      setNewSubcategory({ name: '' });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: string | number) => {
    try {
      await deleteSubcategory(id);
      setSubcategories((prev) => prev.filter((s) => s.id !== id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading subcategories...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Subcategories</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Name"
          value={newSubcategory.name}
          onChange={(e) => setNewSubcategory({ name: e.target.value })}
          required
        />
        <button type="submit">Add</button>
      </form>
      <ul>
        {subcategories.map((s) => (
          <li key={s.id}>
            {s.name}
            <button onClick={() => handleDelete(s.id)} style={{ marginLeft: '1rem' }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
