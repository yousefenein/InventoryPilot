import React, { useEffect, useState } from "react";
import { Card, Button } from "@nextui-org/react";
import SideBar from "../../dashboard_sidebar1/App";

const AccountManagement = () => {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const data = await new Promise((resolve) =>
          setTimeout(() => {
            resolve({
              username: "",
              email: "",
              role: "",
              firstName: "",
              lastName: "",
              department: " ",
            });
          }, 500)
        );
        setUserData(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching user data:", error);
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

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
                <p><strong>Username:</strong> {userData?.username}</p>
                <p><strong>Email:</strong> {userData?.email}</p>
                <p><strong>Role:</strong> {userData?.role}</p>
              </Card>

              <Card className="p-6 shadow-md border">
                <h2 className="text-lg font-semibold mb-2">Personal Information</h2>
                <p><strong>First Name:</strong> {userData?.firstName}</p>
                <p><strong>Last Name:</strong> {userData?.lastName}</p>
                <p><strong>Department:</strong> {userData?.department}</p>
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
