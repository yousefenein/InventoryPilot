import React from "react";
import { useNavigate } from "react-router-dom";
import SideBar from "../../dashboard_sidebar1/App";
import Header from "../../dashboard_sidebar/Header";

const ChangePasswordButton = () => {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate("/change_password")}
      className="bg-blue-600 text-white px-5 py-2 rounded-lg shadow hover:bg-blue-700 transition"
    >
      Change Password
    </button>
  );
};

export default ChangePasswordButton;
