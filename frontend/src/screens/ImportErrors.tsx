import React, { useEffect, useState } from 'react';
import { fetchImportErrors, createImportError, deleteImportError } from '../services/apiEntities.ts';

export default function ImportErrors() {
  const [errors, setErrors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newError, setNewError] = useState<{ message: string }>({ message: '' });

  useEffect(() => {
    fetchImportErrors()
      .then((data) => setErrors(data as any[]))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createImportError(newError);
      setErrors((prev) => [...prev, created]);
      setNewError({ message: '' });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: string | number) => {
    try {
      await deleteImportError(id);
      setErrors((prev) => prev.filter((e) => e.id !== id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading import errors...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Import Errors</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Error Message"
          value={newError.message}
          onChange={(e) => setNewError({ message: e.target.value })}
          required
        />
        <button type="submit">Add</button>
      </form>
      <ul>
        {errors.map((e) => (
          <li key={e.id}>
            {e.message}
            <button onClick={() => handleDelete(e.id)} style={{ marginLeft: '1rem' }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
