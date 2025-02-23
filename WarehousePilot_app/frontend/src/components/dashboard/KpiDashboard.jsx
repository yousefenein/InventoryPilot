import React, { useState } from "react";
// import Header from "../dashboard_sidebar/Header";
 import CycleTime from "./CycleTime";
 import OrderPickingAccuracy from "./OrderPickingAccuracy";
// import StockLevels from "./StockLevels";
 import WarehouseThroughput from "./WarehouseThroughput";
// import OrderFulfillmentRate from "./OrderFulfillmentRate";
// import StockLevelsPreview from "./StockLevelsPreview";
import SideBar from "../dashboard_sidebar1/App";
import NavBar from "../navbar/App";
const KPIDashboard = ({ userData }) => {
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Sidebar */}
      <SideBar userData={userData} isOpen={isSidebarOpen} />

     
      <div className="flex-1 flex flex-col p-6">
        {/* KPI Dashboard Content */}
        {/* <main className="flex-1 p-6"> */}
          {/* Title */}

<h1 className="text-3xl font-bold text-center m-6">KPI Dashboard</h1> 

 {/* Overview Section */}
 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {/* Individual metric cards */}
          <div className="bg-white p-4 shadow rounded-lg">
            <h2 className="text-xl font-semibold">Active Orders</h2>
            <p className="text-3xl font-bold">14k</p>
            <p className="text-green-500">+25%</p>
            
          </div>
          <div className="bg-white p-4 shadow rounded-lg">
            <h2 className="text-xl font-semibold">Completed Orders</h2>
            <p className="text-3xl font-bold">325</p>
            <p className="text-red-500">-25%</p>
          </div>
          <div className="bg-white ps-4 p-4 shadow rounded-lg">
            <h2 className="text-xl font-semibold">Picking Accuracy</h2>
            <div className="accuracy-metrics">
              <OrderPickingAccuracy />
            </div>
         
          </div>
          {/* <div className="bg-white p-4 shadow rounded-lg">
            <h2 className="text-xl font-semibold">Sessions</h2>
            <p className="text-3xl font-bold">13,277</p>
            <p className="text-green-500">+35%</p>
          </div> */}
        </div>

  {/* Graph Section */}
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left graph */}
          <div className="bg-white p-4 shadow rounded-lg flex flex-col h-full">
            <h2 className="text-xl font-semibold">Warehouse Throughput Graph
               
            </h2>
            {/* Placeholder for graph */}
            <div className="h-64 bg-gray-200 flex items-center justify-center">
           
            </div>
          </div>

          {/* Right graph */}
          <div className="bg-white p-4 shadow rounded-lg flex flex-col h-full">
            <h2 className="text-xl font-semibold mb-4">Cycle Time Per Order</h2>
            {/* Placeholder for graph */}
            <div className="h-64 bg-gray-200 flex items-center justify-center">
            
            </div>
          </div>
        </div>

          {/* Details Section */}
          <div className="mt-6 bg-white p-4 shadow rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Details</h2>
          {/* Placeholder for table or additional data */}
          <div className="h-64 bg-gray-200 flex items-center justify-center">
            Table/Data Placeholder
          </div>
        </div>
          

          {/* Cards Container */}
          {/* <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <CycleTime />
            <OrderPickingAccuracy />
            <StockLevels />
            <WarehouseThroughput />
            <OrderFulfillmentRate />
            <StockLevels />
          </div> */}
        {/* </main> */}
      </div>
    </div>
  );
};

export default KPIDashboard;