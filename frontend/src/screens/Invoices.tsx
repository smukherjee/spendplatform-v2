import React, { useEffect, useState } from 'react';
import { fetchInvoices, createInvoice, deleteInvoice } from '../services/apiEntities';

export default function Invoices() {
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newInvoice, setNewInvoice] = useState<{ invoice_number: string; date: string }>({ invoice_number: '', date: '' });

  useEffect(() => {
    fetchInvoices()
      .then((data) => {
        // Handle paginated response
        const invoicesList = data.items || data || [];
        setInvoices(invoicesList as any[]);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createInvoice(newInvoice);
      setInvoices((prev) => [...prev, created]);
      setNewInvoice({ invoice_number: '', date: '' });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: string | number) => {
    try {
      await deleteInvoice(id);
      setInvoices((prev) => prev.filter((inv) => inv.id !== id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading invoices...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Invoices</h2>
      <form onSubmit={handleCreate} style={{ marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Invoice Number"
          value={newInvoice.invoice_number}
          onChange={(e) => setNewInvoice({ ...newInvoice, invoice_number: e.target.value })}
          required
        />
        <input
          type="date"
          placeholder="Date"
          value={newInvoice.date}
          onChange={(e) => setNewInvoice({ ...newInvoice, date: e.target.value })}
          required
        />
        <button type="submit">Add</button>
      </form>
      <ul>
        {invoices.map((inv) => (
          <li key={inv.id}>
            {inv.invoice_number} ({inv.date})
            <button onClick={() => handleDelete(inv.id)} style={{ marginLeft: '1rem' }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
