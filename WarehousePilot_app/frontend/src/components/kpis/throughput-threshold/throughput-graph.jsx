import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import React, { useEffect, useState } from 'react';
import { startOfWeek, format } from 'date-fns';

export default function ThroughputBarGraph({ data, loading, title, isStacked }) {
  const [groupedData, setGroupedData] = useState([]);
  
    /* useEffect - group data by weeks for bar graph */
    useEffect(() => {
      const weeklyData = {};
  
      // Group data by weeks
      data.forEach((entry) => {
        const date = new Date(entry.date);
        const weekStart = startOfWeek(date, { weekStartsOn: 1 }); // Get the Monday of the week
        const weekKey = format(weekStart, 'yyyy-MM-dd'); // Use the Monday's date as the key
  
        if (!weeklyData[weekKey]) {
          weeklyData[weekKey] = { date: weekKey, picked: 0, packed: 0, shipped: 0 };
        }
  
        weeklyData[weekKey].picked += entry.picked || 0;
        weeklyData[weekKey].packed += entry.packed || 0;
        weeklyData[weekKey].shipped += entry.shipped || 0;
      });
  
      // Convert grouped data into an array and sort by date
      const formattedData = Object.values(weeklyData).sort((a, b) => new Date(a.date) - new Date(b.date));
      setGroupedData(formattedData); // Update the grouped data state
    }, [data]);
  
  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
      {loading ? (
        <div className="flex justify-center items-center h-64 dark:text-gray-400">
          <div>Loading...</div>
        </div>
      ) : (
        <>
          {title && <h2 className="text-xl font-semibold mb-4 dark:text-white">{title}</h2>}
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={groupedData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#4B5563" />
              <XAxis 
                dataKey="date" 
                tick={{ fill: '#9CA3AF' }} 
                stroke="#6B7280"
              />
              <YAxis 
                tick={{ fill: '#9CA3AF' }}
                stroke="#6B7280"
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1F2937',
                  borderColor: '#374151',
                  color: '#F3F4F6'
                }}
              />
              <Legend />
              <Bar dataKey="picked" fill="#EF4444" stackId={isStacked ? 'a' : null} />
              <Bar dataKey="packed" fill="#F59E0B" stackId={isStacked ? 'a' : null} />
              <Bar dataKey="shipped" fill="#10B981" stackId={isStacked ? 'a' : null} />
            </BarChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
}