import React from "react";
import SideBar from "../../dashboard_sidebar1/App";
import Header from "../../dashboard_sidebar/Header";

const PersonalInfo = ({ firstName, lastName, department }) => {
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Personal Information</h3>
      <div className="space-y-2 text-gray-700">
        <p><span className="font-medium">First Name:</span> {firstName}</p>
        <p><span className="font-medium">Last Name:</span> {lastName}</p>
        <p><span className="font-medium">Department:</span> {department}</p>
      </div>
    </div>
  );
};

export default PersonalInfo;
