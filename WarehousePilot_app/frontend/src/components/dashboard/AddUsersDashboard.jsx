import React, { useState } from "react";
import SideBar from "../dashboard_sidebar1/App";
// import Header from "../dashboard_sidebar/Header";
import UserForm from "./UseForm";


const AddUsersDashboard = ({ userData }) => {
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!isSidebarOpen);
  };

  return (
    <div>
      {/* Sidebar */}
      <SideBar />

      {/* Main Content */}
      
        {/* Header */}
        {/* <Header userData={userData} toggleSidebar={toggleSidebar} /> */}

        {/* KPI Dashboard Content */}
        <main className="p-6 h-screen my-6">
         

          
           <UserForm />
         
        </main>
      </div>
    
  );
};

export default AddUsersDashboard;

