// the main page of the admin dashboard. The first thing they see when logging in.
// route: /admin_dashboard

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Dashboard from './Dashboard';

function AdminDashboard() {
  const [userData, setUserData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const verifyAdminAccess = async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
            return;
        }

        try {
            const response = await axios.get('http://127.0.0.1:8000/auth/profile/', {
                headers: { Authorization: `Bearer ${token}` },
            });
            
            if (response.data.role !== 'admin') {
                // Redirect based on role
                if (response.data.role === 'manager') {
                    navigate('/manager_dashboard');
                } else {
                    navigate('/dashboard');
                }
                return;
            }
            
            setUserData(response.data);
        } catch (error) {
            console.error('Error fetching user data:', error);
            navigate('/login');
        }
    };

    verifyAdminAccess();
}, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };


  return (
    <div>
      <Dashboard userData={userData} />
    </div>
  );
}

export default AdminDashboard;