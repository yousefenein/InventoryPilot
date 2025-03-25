import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardBody } from "@heroui/card";
import axios from 'axios';
import React, { useEffect, useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default function ThroughputBarGraph() {
  const [fetchedData, setFetchedData] = useState([]); //raw data from API
  const [data, setData] = useState([]); //formatted data for ThroughputBarGraph
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /* fetchData: fetch and format data for ThroughputBarGraph */
  const fetchData = async () => {
    try {
      // Get authorization token from local storage
      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authorization token found");
        setLoading(false);
        return;
      }

      // Backend API call to get throughput data
      const response = await axios.get(
        `${API_BASE_URL}/orders/`, //TODO: Change this to throughput path
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );
      setFetchedData(response.data);

      // Format data for ThroughputBarGraph
      const formattedData = fetchedData.map((item) => {
        return {
          week: item.week,
          picked: item.picked,
          packed: item.packed,
          shipped: item.shipped,
        };
      });
      setData(formattedData);
      setLoading(false);
    }
    catch (error) {
      setError(error.message);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (data.length === 0) { // TODO: Remove this when API is ready
    setData([
      { week: 'Week 1', picked: 400, packed: 300, shipped: 200 },
      { week: 'Week 2', picked: 500, packed: 400, shipped: 300 },
      { week: 'Week 3', picked: 600, packed: 500, shipped: 400 },
      { week: 'Week 4', picked: 700, packed: 600, shipped: 500 },
    ]);
  }

  return (
    <Card className="p-4 shadow-lg rounded-2xl">
      <CardBody>
        <h2 className="text-xl font-semibold mb-4">Throughput per Week</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="picked" fill="#8884d8" stackId="a" /> {/* TODO: Change colors */}
            <Bar dataKey="packed" fill="#82ca9d" stackId="a" />
            <Bar dataKey="shipped" fill="#ffc658" stackId="a" />
          </BarChart>
        </ResponsiveContainer>
      </CardBody>
    </Card>
  );
}