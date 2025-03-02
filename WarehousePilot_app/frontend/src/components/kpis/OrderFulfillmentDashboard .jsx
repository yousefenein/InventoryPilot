import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, 
  Tooltip, Legend, LineChart, Line, XAxis, YAxis, 
  CartesianGrid, BarChart, Bar
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];
const API_BASE_URL = "http://127.0.0.1:8000/kpi_dashboard"; // Change to your backend URL

const OrderFulfillmentDashboard = () => {
  const [data, setData] = useState([]);
  const [currentPeriod, setCurrentPeriod] = useState(null);
  const [filterType, setFilterType] = useState('month');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0]); // Default to today
  const [loading, setLoading] = useState(true);
  const [chartType, setChartType] = useState('pie');
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

      console.log("API Response:", response.data); // Debugging log

      if (!Array.isArray(response.data) || response.data.length === 0) {
        setData([]);
        setCurrentPeriod(null);
      } else {
        setData(response.data);
        setCurrentPeriod(response.data[response.data.length - 1]); // Last period
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

  const prepareCircularData = (periodData) => {
    if (!periodData) return [];

    return [
      { name: 'Started', value: periodData.orders_started || 0 },
      { name: 'Partially Fulfilled', value: periodData.partially_fulfilled || 0 },
      { name: 'Fully Fulfilled', value: periodData.fully_fulfilled || 0 },
      { 
        name: 'Not Started', 
        value: Math.max(0, (periodData.total_orders || 0) - (periodData.orders_started || 0) - (periodData.partially_fulfilled || 0) - (periodData.fully_fulfilled || 0))
      }
    ];
  };

  const prepareTrendData = () => {
    return data.map(period => ({
      period: period.period,
      started: calculatePercentage(period.orders_started, period.total_orders),
      partial: calculatePercentage(period.partially_fulfilled, period.total_orders),
      fulfilled: calculatePercentage(period.fully_fulfilled, period.total_orders)
    }));
  };

  const calculatePercentage = (value, total) => {
    if (!total || total === 0) return 0;
    return Math.round((value / total) * 100);
  };

  return (
    <div className="p-6 bg-gray-50 rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">Order Fulfillment Dashboard</h2>
        <div className="flex space-x-4">
          <select value={filterType} onChange={(e) => setFilterType(e.target.value)} className="border rounded-md px-2 py-1">
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
          <select value={chartType} onChange={(e) => setChartType(e.target.value)} className="border rounded-md px-2 py-1">
            <option value="pie">Pie Chart</option>
            <option value="bar">Bar Chart</option>
            <option value="line">Line Chart</option>
          </select>
        </div>
      </div>

      {error ? (
        <div className="text-red-500 text-center">{error}</div>
      ) : loading ? (
        <div className="flex justify-center items-center h-64">Loading data...</div>
      ) : currentPeriod ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <h3 className="text-lg font-medium mb-4">Current Period: {currentPeriod?.period}</h3>
            <div className="h-64">
              {chartType === 'pie' && (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={prepareCircularData(currentPeriod)} cx="50%" cy="50%" outerRadius={80} fill="#8884d8" label>
                      {prepareCircularData(currentPeriod).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
              {chartType === 'bar' && (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={prepareCircularData(currentPeriod)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              )}
              {chartType === 'line' && (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={prepareTrendData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="started" stroke="#0088FE" />
                    <Line type="monotone" dataKey="partial" stroke="#FFBB28" />
                    <Line type="monotone" dataKey="fulfilled" stroke="#00C49F" />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-gray-500 text-center">No data available</div>
      )}
    </div>
  );
};

export default OrderFulfillmentDashboard;
