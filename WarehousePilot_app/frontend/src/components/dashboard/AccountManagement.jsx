import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import NavBar from "../navbar/App";
import SideBar from "../dashboard_sidebar1/App";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;


function AccountManagement() {
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

    return (
      <div>
        {/* Sidebar */}
        <SideBar />
        <NavBar/>
        {/* Main Content */}
        <div className="flex-1 p-6">
        <div className="ml-4">
          {/* Header Section */}
          <div className="mb-4">
            <h1 className="text-2xl lg:text-3xl font-bold text-gray-800 mt-2 lg:mt-4 mb-2">
                Account Management
            </h1>
            <p className="text-base lg:text-lg text-gray-600">
                This is the overview page where you can view your account details.
            </p>
        </div>



          {/* Information Section */}
          {userData ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Basic Information */}
            <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Basic Information</h2>
              <div className="space-y-3 text-gray-700">
                <p>
                  <span className="font-medium text-gray-600">Username:</span>
                  <span className="ml-2 font-semibold text-gray-900">{userData.username}</span>
                </p>
                <p>
                  <span className="font-medium text-gray-600">Email:</span>
                  <span className="ml-2 font-semibold text-gray-900">{userData.email}</span>
                </p>
                <p>
                  <span className="font-medium text-gray-600">Role:</span>
                  <span className="ml-2 font-semibold text-gray-900 capitalize">{userData.role}</span>
                </p>
              </div>
            </div>
          
            {/* Personal Information */}
            <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Personal Information</h2>
              <div className="space-y-3 text-gray-700">
                <p>
                  <span className="font-medium text-gray-600">First Name:</span>
                  <span className="ml-2 font-semibold text-gray-900">{userData.first_name}</span>
                </p>
                <p>
                  <span className="font-medium text-gray-600">Last Name:</span>
                  <span className="ml-2 font-semibold text-gray-900">{userData.last_name}</span>
                </p>
                <p>
                  <span className="font-medium text-gray-600">Department:</span>
                  <span className="ml-2 font-semibold text-gray-900">{userData.department}</span>
                </p>
              </div>
            </div>
          </div>
          
          
          ) : (
            <p className="text-red-500">Error loading user data.</p>
          )}

          {/* Action Button Section */}
          <div className="mt-6 flex justify-center lg:justify-start">
            <button
              type="button"
              className="px-6 py-3 text-white bg-black rounded-lg shadow transition duration-300"
              onClick={() => navigate("/change_password")}
            >
              Change Password
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AccountManagement;