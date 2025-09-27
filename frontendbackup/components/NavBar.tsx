import React from 'react';
import { Link } from 'react-router-dom';

export default function NavBar() {
  return (
    <nav style={{ padding: '1rem', background: '#f5f5f5', borderBottom: '1px solid #ddd' }}>
      <Link to="/">Dashboard</Link> |{' '}
      <Link to="/invoices">Invoices</Link> |{' '}
      <Link to="/suppliers">Suppliers</Link> |{' '}
      <Link to="/business-units">Business Units</Link> |{' '}
      <Link to="/regions">Regions</Link> |{' '}
      <Link to="/roles">Roles</Link> |{' '}
      <Link to="/users">Users</Link> |{' '}
      <Link to="/clients">Clients</Link> |{' '}
      <Link to="/subcategories">Subcategories</Link> |{' '}
      <Link to="/unit-of-measure">Unit Of Measure</Link> |{' '}
      <Link to="/currency">Currency</Link> |{' '}
      <Link to="/import-errors">Import Errors</Link> |{' '}
      <Link to="/reporting">Reporting</Link> |{' '}
      <Link to="/client-settings">Client Settings</Link> |{' '}
      <Link to="/settings">Settings</Link>
    </nav>
  );
}
