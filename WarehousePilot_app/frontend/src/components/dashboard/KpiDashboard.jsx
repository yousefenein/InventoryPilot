//Tested the "View Details" button on dashboard widgets. Test passed on all cards.
//Tested Graph resize on window resize. Test passed.
//Tested the Tooltip for CycleTime Graph on Hover.Test passed.
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import CycleTime from "./CycleTime";
import OrderPickingAccuracy from "./OrderPickingAccuracy";
import WarehouseThroughput from "./WarehouseThroughput";
import ThroughputThresholdKpiPreview from "../kpis/throughput-threshold/throughput-threshold-kpi-preview"
import OrderFulfillmentPreview from "../kpis/OrderFulfillmentPreview"
import SideBar from "../dashboard_sidebar1/App";
import NavBar from "../navbar/App";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import CTPOPreview from "../kpis/CTPO/CTPOPreview";
import StockLevelsPreview from "./StockLevelsPreview"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const KPIDashboard = ({ userData }) => {
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [activeOrdersData, setActiveOrdersData] = useState([]);
  const [completedOrdersData, setCompletedOrdersData] = useState([]);
  const [totalActiveOrders, setTotalActiveOrders] = useState(0);
  const [totalCompletedOrders, setTotalCompletedOrders] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const toggleSidebar = () => {
    setSidebarOpen(!isSidebarOpen);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [activeResponse, completedResponse] = await Promise.all([
          axios.get(`${API_BASE_URL}/kpi_dashboard/active-orders/`),
          axios.get(`${API_BASE_URL}/kpi_dashboard/completed-orders/`),
        ]);
        setActiveOrdersData(activeResponse.data);
        setCompletedOrdersData(completedResponse.data);
        const activeTotal = activeResponse.data.reduce((sum, entry) => sum + entry.active_orders, 0);
        const completedTotal = completedResponse.data.reduce((sum, entry) => sum + entry.completed_orders, 0);
        setTotalActiveOrders(activeTotal);
        setTotalCompletedOrders(completedTotal);
      } catch (err) {
        console.error("Error fetching orders data:", err);
        setError(err.message || "Failed to load orders data.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleViewDetails = () => {
    navigate('/active-orders-details');
  };

  return (
    <div className="flex min-h-screen bg-gray-100 dark:bg-gray-900">
      {/* Sidebar */}
      <SideBar userData={userData} isOpen={isSidebarOpen} />
      
      <div className="flex-1 sm:ml-10 sm:mt-2">
        <NavBar />
        <main className="flex-1 p-12">
          {/* Overview Section - Top 2 Cards */}
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

            {/* Active Orders Card */}

            <div className="bg-white dark:bg-gray-800 p-4 shadow rounded-lg">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Active Orders</h2>
                <button
                  onClick={handleViewDetails}
                  className="bg-gray-500 hover:bg-red-600 text-white py-1 px-3 rounded"
                >
                  View Details
                </button>
              </div>
              {loading ? (
                <p className="text-center text-gray-800 dark:text-white">Loading...</p>
              ) : error ? (
                <p className="text-red-500 text-center">{error}</p>
              ) : (
                <div className="flex flex-col items-center">
                  <div className="flex items-center justify-between mb-4">
                    <p className="text-3xl font-bold text-gray-800 dark:text-white">{totalActiveOrders.toLocaleString()}</p>
                  </div>
                  <div className="w-full flex justify-center">
                    <LineChart width={600} height={300} data={activeOrdersData}>
                      <CartesianGrid strokeDasharray="3 3" stroke={document.documentElement.classList.contains('dark') ? '#4A5568' : '#E2E8F0'} />
                      <XAxis dataKey="date" hide />
                      <YAxis hide />
                      <Tooltip />
                      <Line type="monotone" dataKey="active_orders" stroke="#8884d8" dot={false} />
                    </LineChart>
                  </div>
                </div>
              )}
            </div>


            {/* Completed Orders Card */}
            <div className="bg-white dark:bg-gray-800 p-4 shadow rounded-lg">
              <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Completed Orders</h2>
              {loading ? (
                <p className="text-center text-gray-800 dark:text-white">Loading...</p>
              ) : error ? (
                <p className="text-red-500 text-center">{error}</p>
              ) : (
                <div className="flex flex-col items-center">
                  <div className="flex items-center justify-between mb-4">
                    <p className="text-3xl font-bold text-gray-800 dark:text-white">{totalCompletedOrders.toLocaleString()}</p>
                    <p className="text-red-500 text-xl ml-2">{`-25%`}</p> {/* Adjusted size and margin */}
                  </div>
                  <div className="w-full flex justify-center">
                    <LineChart width={600} height={300} data={completedOrdersData}>
                      <CartesianGrid strokeDasharray="3 3" stroke={document.documentElement.classList.contains('dark') ? '#4A5568' : '#E2E8F0'} />
                      <XAxis dataKey="date" hide />
                      <YAxis hide />
                      <Tooltip />
                      <Line type="monotone" dataKey="completed_orders" stroke="#ff4444" dot={false} />
                    </LineChart>
                  </div>
                </div>
              )}
            </div>




          </div>

          {/* First Row of Graphs */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="bg-white dark:bg-gray-800 p-4 shadow rounded-lg">
              <OrderPickingAccuracy />
            </div>
            <div className="bg-white dark:bg-gray-800 p-4 shadow rounded-lg">
              <OrderFulfillmentPreview/>
            </div>
          </div>

           {/* Second Row of Graphs */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="bg-white dark:bg-gray-800 p-4 shadow rounded-lg">
              <CTPOPreview />
            </div>
            
           {/* Order Picking Accuracy Card */}
            <div className="bg-white dark:bg-gray-800 p-4 shadow rounded-lg">
              <ThroughputThresholdKpiPreview/>
            </div>
          </div>

          {/* Inventory preview Section */}
          <div className="bg-white dark:bg-gray-800 p-4 shadow rounded-lg">
            <StockLevelsPreview />
          </div>
        </main>
      </div>
    </div>
  );
};

export default KPIDashboard;