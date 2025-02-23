import React, { useEffect, useState } from "react";
import { Card, Button } from "@nextui-org/react";
import axios from "axios";
import SideBar from "../../dashboard_sidebar1/App";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const AccountManagement = () => {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          console.error("No authorization token found.");
          setLoading(false);
          return;
        }

        const response = await axios.get(`${API_BASE_URL}/auth/profile/`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        setUserData(response.data);  
        setLoading(false);
      } catch (error) {
        console.error("Error fetching user data:", error);
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading user information...</div>;
  }

  return (
    <div className="flex h-full">
      <SideBar />
      <div className="flex-1">
        <div className="mt-16 p-8">
          <div className="flex flex-col gap-6">
            <h1 className="text-2xl font-bold">Account Management</h1>
            <p className="text-lg text-gray-500 mb-6">
              This is the overview page where you can view your account details.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="p-6 shadow-md border">
                <h2 className="text-lg font-semibold mb-2">Basic Information</h2>
                <p><strong>Username:</strong> {userData?.username || "N/A"}</p>
                <p><strong>Email:</strong> {userData?.email || "N/A"}</p>
                <p><strong>Role:</strong> {userData?.role || "N/A"}</p>
              </Card>

              <Card className="p-6 shadow-md border">
                <h2 className="text-lg font-semibold mb-2">Personal Information</h2>
                <p><strong>First Name:</strong> {userData?.first_name || "N/A"}</p>
                <p><strong>Last Name:</strong> {userData?.last_name || "N/A"}</p>
                <p><strong>Department:</strong> {userData?.department || "N/A"}</p>
              </Card>
            </div>

            <div className="mt-6">
              <Button color="primary" className="w-full md:w-auto">
                Change Password
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccountManagement;
