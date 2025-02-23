import React from "react";
import SideBar from "../../dashboard_sidebar1/App";
import Header from "../../dashboard_sidebar/Header";

const BasicInfo = ({ username, email, role }) => {
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Basic Information</h3>
      <div className="space-y-2 text-gray-700">
        <p><span className="font-medium">Username:</span> {username}</p>
        <p><span className="font-medium">Email:</span> {email}</p>
        <p><span className="font-medium">Role:</span> {role}</p>
      </div>
    </div>
  );
};

export default BasicInfo;
