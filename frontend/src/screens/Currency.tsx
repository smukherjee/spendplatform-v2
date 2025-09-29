import React, { useEffect, useState } from 'react';
import { fetchCurrencies, createCurrency, deleteCurrency } from '../services/apiEntities';

export default function Currency() {
  const [currencies, setCurrencies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newCurrency, setNewCurrency] = useState<{ name: string }>({ name: '' });

  useEffect(() => {
    fetchCurrencies()
      .then((data) => {
        // Handle paginated response
        const currenciesList = data.items || data || [];
        setCurrencies(currenciesList as any[]);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createCurrency(newCurrency);
      setCurrencies((prev) => [...prev, created]);
      setNewCurrency({ name: '' });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: string | number) => {
    try {
      await deleteCurrency(id);
      setCurrencies((prev) => prev.filter((c) => c.id !== id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading currencies...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Currencies</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Name"
          value={newCurrency.name}
          onChange={(e) => setNewCurrency({ name: e.target.value })}
          required
        />
        <button type="submit">Add</button>
      </form>
      <ul>
        {currencies.map((c) => (
          <li key={c.id}>
            {c.name}
            <button onClick={() => handleDelete(c.id)} style={{ marginLeft: '1rem' }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
