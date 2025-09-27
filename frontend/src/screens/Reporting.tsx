import React, { useEffect, useState } from 'react';
import { fetchReports, createReport, deleteReport } from '../services/apiEntities.ts';

export default function Reporting() {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newReport, setNewReport] = useState<{ name: string }>({ name: '' });

  useEffect(() => {
    fetchReports()
      .then((data) => setReports(data as any[]))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createReport(newReport);
      setReports((prev) => [...prev, created]);
      setNewReport({ name: '' });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: string | number) => {
    try {
      await deleteReport(id);
      setReports((prev) => prev.filter((r) => r.id !== id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading reports...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Reports</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Name"
          value={newReport.name}
          onChange={(e) => setNewReport({ name: e.target.value })}
          required
        />
        <button type="submit">Add</button>
      </form>
      <ul>
        {reports.map((r) => (
          <li key={r.id}>
            {r.name}
            <button onClick={() => handleDelete(r.id)} style={{ marginLeft: '1rem' }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
