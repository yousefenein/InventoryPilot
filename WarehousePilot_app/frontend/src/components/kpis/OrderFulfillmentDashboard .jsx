import React, { useState, useEffect } from 'react';
import axios from 'axios';
import OrderFulfillmentChart from './OrderFulfillmentChart';
import OrderFulfillmentTable from './OrderFulfillmentTable';
import NavBar from "../navbar/App";
const API_BASE_URL = "http://127.0.0.1:8000/kpi_dashboard"; // Update with your backend URL

const OrderFulfillmentDashboard = () => {
  const [data, setData] = useState([]);
  const [currentPeriod, setCurrentPeriod] = useState(null);
  const [filterType, setFilterType] = useState('month');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, [filterType, selectedDate]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authorization token found");
        setLoading(false);
        return;
      }

      const response = await axios.get(
        `${API_BASE_URL}/order-fulfillment-rate/?filter=${filterType}&date=${selectedDate}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!Array.isArray(response.data) || response.data.length === 0) {
        setData([]);
        setCurrentPeriod(null);
      } else {
        setData(response.data);
        setCurrentPeriod(response.data[response.data.length - 1]);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      setError("Failed to fetch data");
      setData([]);
      setCurrentPeriod(null);
    } finally {
      setLoading(false);
    }
  };

  // Function to format the date for display
  const formatPeriodDate = (dateStr) => {
    if (!dateStr) return "N/A";
    
    const date = new Date(dateStr);
    const options = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    };
    
    if (filterType === 'month') {
      options.day = undefined;
    } else if (filterType === 'week') {
      return `Week of ${date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;
    }
    
    return date.toLocaleDateString(undefined, options);
  };

  return (
     <div className="min-h-screen bg-gray-50">
          {/* Navbar */}
          <NavBar />
          <div className="max-w-screen mx-auto px-10 py-8">
    <div className="p-6 bg-gray-50 rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">Order Fulfillment Dashboard</h2>
        <div className="flex space-x-4">
          <select 
            value={filterType} 
            onChange={(e) => setFilterType(e.target.value)} 
            className="border rounded-md px-2 py-1"
          >
            <option value="day">Daily</option>
            <option value="week">Weekly</option>
            <option value="month">Monthly</option>
          </select>
          <input 
            type="date" 
            value={selectedDate} 
            onChange={(e) => setSelectedDate(e.target.value)} 
            className="border rounded-md px-2 py-1"
          />
        </div>
      </div>

      {error ? (
        <div className="text-red-500 text-center p-4 bg-white rounded-lg shadow-sm">{error}</div>
      ) : loading ? (
        <div className="flex justify-center items-center h-64 bg-white rounded-lg shadow-sm p-4">
          <div className="animate-pulse text-gray-600">Loading data...</div>
        </div>
      ) : currentPeriod ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Order Fulfillment Chart Component */}
          <OrderFulfillmentChart currentPeriod={currentPeriod} />

          {/* Order Fulfillment Table Component */}
          <OrderFulfillmentTable 
            currentPeriod={currentPeriod} 
            formatPeriodDate={formatPeriodDate}
            filterType={filterType}
          />
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center p-8 bg-white rounded-lg shadow-sm text-center">
          <div className="text-5xl mb-4">🔍</div>
          <h3 className="text-xl font-medium text-gray-800 mb-2">Hmm, nothing to see here!</h3>
          <p className="text-gray-600">We couldn't find any order data for the selected period.</p>
          <p className="text-gray-500 text-sm mt-2">Try selecting a different date or time range.</p>
          <p className="text-gray-500 text-sm mt-2">  <b>January 4th 2025</b> could be a good example </p>
        </div>
      )}
    </div>
    </div>
    </div>
  );
};

export default OrderFulfillmentDashboard;