// the main page of the admin dashboard. The first thing they see when logging in.
// route: /admin_dashboard

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Dashboard from './Dashboard';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// logging: push log messages from frontend back to django (backend)
const logging = async (level, message) => {
  try {
      await axios.post(`${API_BASE_URL}/logging/log/`, { level, message });
  } catch (error) {
      console.error("Failed to send log to Django", error);
  }
};

function AdminDashboard() {
  const [userData, setUserData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserData = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const response = await axios.get(`${API_BASE_URL}/auth/profile/`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          setUserData(response.data);
        } catch (error) {
          logging('error', `Failed to fetch user data in the Admin Dashboard page in the client - ${error}`);
          console.error('Error fetching user data:', error);
        }
      }
    };
    fetchUserData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    logging('info', 'User has logged out');
    navigate('/');
  };


  return (
    <div>
      <Dashboard userData={userData} />
    </div>
  );
}

export default AdminDashboard;