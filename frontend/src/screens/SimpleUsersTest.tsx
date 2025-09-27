import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';

interface SimpleUser {
  id: string;
  name: string;
  email: string;
}

export default function SimpleUsersTest() {
  const [users, setUsers] = useState<SimpleUser[]>([]);

  useEffect(() => {
    console.log('🧪 Loading simple test data...');
    const testUsers: SimpleUser[] = [
      { id: 'test-1', name: 'John Doe', email: 'john@example.com' },
      { id: 'test-2', name: 'Jane Smith', email: 'jane@example.com' },
      { id: 'test-3', name: 'Bob Johnson', email: 'bob@example.com' }
    ];
    
    console.log('🧪 Test users:', testUsers);
    setUsers(testUsers);
  }, []);

  console.log('🧪 Rendering with users:', users);

  return (
    <div className="p-4">
      <h1>Simple Users Test</h1>
      <p>Users count: {users.length}</p>
      
      <DataTable 
        key="simple-test-table"
        value={users} 
        dataKey="id"
        className="p-datatable-sm"
      >
        <Column key="test-id" field="id" header="ID" />
        <Column key="test-name" field="name" header="Name" />
        <Column key="test-email" field="email" header="Email" />
      </DataTable>
    </div>
  );
}