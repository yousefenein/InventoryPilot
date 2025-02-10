import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Dashboard from './Dashboard';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function QADashboard() {
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
          console.error('Error fetching user data:', error);
        }
      } else {
        navigate('/'); 
      }
    };
    fetchUserData();
  }, [navigate]);

  return (
    <div>
      <Dashboard userData={userData} />
      <h1>Hello QA Dashboard</h1>
    </div>
  );
}

export default QADashboard;
