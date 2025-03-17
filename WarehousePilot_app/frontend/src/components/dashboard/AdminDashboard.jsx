import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import NavBar from "../navbar/App";
import SideBar from "../dashboard_sidebar1/App";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function AdminDashboard() {
  const [userData, setUserData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserData = async () => {
      const token = localStorage.getItem("token");
      if (token) {
        try {
          const response = await axios.get(`${API_BASE_URL}/auth/profile/`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          setUserData(response.data);
        } catch (error) {
          console.error("Error fetching user data:", error);
        }
      }
    };
    fetchUserData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <div>
      {/* Sidebar */}
      <SideBar/>
      <NavBar/>


      {/* Main Content */}
      <div className="flex-1 p-6">
        <div className="ml-4">
          {/* Header Section */}
          <div className="mb-4">
            <h1 className="text-2xl lg:text-3xl font-bold text-gray-800 mt-2 lg:mt-4 mb-2">
              Welcome, {userData ? userData.first_name : "Loading..."}!
            </h1>

          </div>

          {/* User Information Section */}
          {userData ? (
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">User Details</h2>
              <p className="text-gray-700">
                <strong>Username:</strong> {userData.username}
              </p>
              <p className="text-gray-700">
                <strong>Email:</strong> {userData.email}
              </p>
              <p className="text-gray-700">
                <strong>Role:</strong> {userData.role}
              </p>
              <p className="text-gray-700">
                <strong>Department:</strong> {userData.department}
              </p>
            </div>
          ) : (
            <p className="text-red-500">Error loading user data.</p>
          )}

          {/* Logout Button */}
          <div className="mt-6 flex justify-center lg:justify-start">
            <button
              className="px-6 py-3 text-white bg-black rounded-lg shadow transition duration-300"
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
