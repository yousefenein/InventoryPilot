import React, { useState, useEffect } from "react";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";
import axios from 'axios';

const COLORS = ["#950606", "#ca3433"];

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const OrderPickingAccuracy = () => {
  const [data, setData] = useState([
    { name: "Accurate Picks", value: 0 },
    { name: "Inaccurate Picks", value: 0 },
  ]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [accuracyPercentage, setAccuracyPercentage] = useState(0); 
  const [totalPicks, setTotalPicks] = useState(0);
  const [targetAccuracy, setTargetAccuracy] = useState(99); // State for target accuracy
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token'); // Retrieve token
        const response = await axios.get(`${API_BASE_URL}/kpi_dashboard/order-picking-accuracy/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const result = response.data; // Use response.data for axios
// console.log(result)
const accurate = result.inaccurate_picks || 0; //they were fetched in the inverse order so I fixed them here
const inaccurate = result.accurate_picks || 0;
const total = accurate + inaccurate;
        // Update the data state
        setData([
          { name: "Accurate Picks", value: accurate },
          { name: "Inaccurate Picks", value: inaccurate },
        ]);

        setTotalPicks(total);
        setAccuracyPercentage(total > 0 ? ((accurate / total) * 100).toFixed(1) : 0);

      } catch (error) {
        console.error("Error fetching data:", error);
        setError("Failed to fetch data. Please try again later."); // Set error message
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Calculate the accuracy percentage
  // const totalPicks = data[0].value + data[1].value;
  // const accuracyPercentage = totalPicks > 0 ? ((data[0].value / totalPicks) * 100).toFixed(2) : 0;

  return (
    <div className="flex flex-col">
    <div >
      <p className="text-3xl font-bold">{totalPicks.toLocaleString()}</p>
      <p className={`${accuracyPercentage >= targetAccuracy ? 'text-green-500' : 'text-red-500'}`}>
        {accuracyPercentage}%
      </p>
    </div>
    <div className="bg-white">
      {loading ? (
        <p className="text-center">Loading...</p>
      ) : error ? (
        <p className="text-red-500 text-center">{error}</p>
      ) : (
        <>
          {/* Chart */}
          <PieChart width={300} height={200}>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={80}
              fill="#950606"
              label
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>

          {/* Current data and target */}
          {/* <p className="text-center mt-2 text-gray-600">
            Current: <span className="text-green-600">{accuracyPercentage}%</span>, Target:{" "}
            <span className="text-blue-600">{targetAccuracy}%</span>
          </p> */}
        </>
      )}
    </div>
    </div>
  );
};

export default OrderPickingAccuracy;