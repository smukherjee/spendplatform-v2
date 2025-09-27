import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function UserEdit() {
  const navigate = useNavigate();
  
  useEffect(() => {
    // Redirect to Users screen since edit functionality is integrated there
    navigate('/users');
  }, [navigate]);

  return <div>Redirecting to Users...</div>;
}
