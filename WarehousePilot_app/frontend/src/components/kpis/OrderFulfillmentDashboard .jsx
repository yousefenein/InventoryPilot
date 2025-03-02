// import React, { useState, useEffect } from 'react';
// import { 
//   PieChart, Pie, Cell, ResponsiveContainer, 
//   Tooltip, Legend, LineChart, Line, XAxis, YAxis, 
//   CartesianGrid, BarChart, Bar
// } from 'recharts';

// const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

// const OrderFulfillmentDashboard = () => {
//   const [data, setData] = useState([]);
//   const [currentPeriod, setCurrentPeriod] = useState(null);
//   const [filterType, setFilterType] = useState('month');
//   const [loading, setLoading] = useState(true);
//   const [chartType, setChartType] = useState('pie');

//   useEffect(() => {
//     fetchData();
//   }, [filterType]);

//   const fetchData = async () => {
//     setLoading(true);
//     try {
//       const response = await fetch(`/kpi_dashboard/order-fulfillment-rate/?filter=${filterType}`);
//       const result = await response.json();
//       setData(result);
      
//       // Set current period to the latest one
//       if (result.length > 0) {
//         setCurrentPeriod(result[result.length - 1]);
//       }
      
//       setLoading(false);
//     } catch (error) {
//       console.error("Error fetching data:", error);
//       setLoading(false);
//     }
//   };

//   const prepareCircularData = (periodData) => {
//     if (!periodData) return [];
    
//     return [
//       { name: 'Started', value: periodData.orders_started },
//       { name: 'Partially Fulfilled', value: periodData.partially_fulfilled },
//       { name: 'Fully Fulfilled', value: periodData.fully_fulfilled },
//       { 
//         name: 'Not Started', 
//         value: Math.max(
//           0, 
//           periodData.total_orders - 
//           periodData.orders_started - 
//           periodData.partially_fulfilled - 
//           periodData.fully_fulfilled
//         ) 
//       }
//     ];
//   };

//   const prepareTrendData = () => {
//     return data.map(period => ({
//       period: period.period,
//       started: calculatePercentage(period.orders_started, period.total_orders),
//       partial: calculatePercentage(period.partially_fulfilled, period.total_orders),
//       fulfilled: calculatePercentage(period.fully_fulfilled, period.total_orders)
//     }));
//   };

//   const calculatePercentage = (value, total) => {
//     if (!total) return 0;
//     return Math.round((value / total) * 100);
//   };

//   const CustomTooltip = ({ active, payload }) => {
//     if (active && payload && payload.length) {
//       return (
//         <div className="bg-white p-4 shadow-md rounded-md border border-gray-200">
//           <p className="font-semibold text-gray-700">{`${payload[0].name}: ${payload[0].value}`}</p>
//           <p className="text-gray-600">{`${calculatePercentage(payload[0].value, currentPeriod?.total_orders)}% of total`}</p>
//         </div>
//       );
//     }
//     return null;
//   };

//   return (
//     <div className="p-6 bg-gray-50 rounded-lg shadow-sm">
//       <div className="flex justify-between items-center mb-6">
//         <h2 className="text-xl font-semibold text-gray-800">Order Fulfillment Dashboard</h2>
        
//         <div className="flex space-x-4">
//           <div className="flex items-center space-x-2">
//             <label className="text-sm font-medium text-gray-700">Period:</label>
//             <select 
//               className="border border-gray-300 rounded-md px-2 py-1 text-sm"
//               value={filterType}
//               onChange={(e) => setFilterType(e.target.value)}
//             >
//               <option value="day">Daily</option>
//               <option value="week">Weekly</option>
//               <option value="month">Monthly</option>
//             </select>
//           </div>
          
//           <div className="flex items-center space-x-2">
//             <label className="text-sm font-medium text-gray-700">Chart Type:</label>
//             <select 
//               className="border border-gray-300 rounded-md px-2 py-1 text-sm"
//               value={chartType}
//               onChange={(e) => setChartType(e.target.value)}
//             >
//               <option value="pie">Pie Chart</option>
//               <option value="line">Line Chart</option>
//               <option value="bar">Bar Chart</option>
//             </select>
//           </div>
//         </div>
//       </div>
      
//       {loading ? (
//         <div className="flex justify-center items-center h-64">
//           <p>Loading data...</p>
//         </div>
//       ) : data.length === 0 ? (
//         <div className="flex justify-center items-center h-64">
//           <p>No data available for the selected period.</p>
//         </div>
//       ) : (
//         <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
//           {/* Current Period Stats */}
//           <div className="bg-white p-4 rounded-lg shadow-sm">
//             <h3 className="text-lg font-medium text-gray-700 mb-4">
//               Current Period: {currentPeriod?.period}
//             </h3>
//             <div className="h-64">
//               {chartType === 'pie' && (
//                 <ResponsiveContainer width="100%" height="100%">
//                   <PieChart>
//                     <Pie
//                       data={prepareCircularData(currentPeriod)}
//                       cx="50%"
//                       cy="50%"
//                       innerRadius={60}
//                       outerRadius={80}
//                       fill="#8884d8"
//                       paddingAngle={5}
//                       dataKey="value"
//                       label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
//                     >
//                       {prepareCircularData(currentPeriod).map((entry, index) => (
//                         <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
//                       ))}
//                     </Pie>
//                     <Tooltip content={<CustomTooltip />} />
//                     <Legend />
//                   </PieChart>
//                 </ResponsiveContainer>
//               )}
              
//               {chartType === 'bar' && (
//                 <ResponsiveContainer width="100%" height="100%">
//                   <BarChart
//                     data={prepareCircularData(currentPeriod)}
//                     margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
//                   >
//                     <CartesianGrid strokeDasharray="3 3" />
//                     <XAxis dataKey="name" />
//                     <YAxis />
//                     <Tooltip />
//                     <Legend />
//                     <Bar dataKey="value" name="Orders" fill="#8884d8" />
//                   </BarChart>
//                 </ResponsiveContainer>
//               )}
//             </div>
//             <div className="mt-4 grid grid-cols-2 gap-4">
//               <div className="bg-blue-50 p-3 rounded-md">
//                 <p className="text-sm text-gray-600">Total Orders</p>
//                 <p className="text-xl font-semibold">{currentPeriod?.total_orders}</p>
//               </div>
//               <div className="bg-green-50 p-3 rounded-md">
//                 <p className="text-sm text-gray-600">Fulfillment Rate</p>
//                 <p className="text-xl font-semibold">
//                   {calculatePercentage(currentPeriod?.fully_fulfilled, currentPeriod?.total_orders)}%
//                 </p>
//               </div>
//             </div>
//           </div>
          
//           {/* Trend Over Time */}
//           <div className="bg-white p-4 rounded-lg shadow-sm">
//             <h3 className="text-lg font-medium text-gray-700 mb-4">
//               Fulfillment Rate Trend
//             </h3>
//             <div className="h-64">
//               <ResponsiveContainer width="100%" height="100%">
//                 <LineChart
//                   data={prepareTrendData()}
//                   margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
//                 >
//                   <CartesianGrid strokeDasharray="3 3" />
//                   <XAxis dataKey="period" />
//                   <YAxis label={{ value: 'Percentage (%)', angle: -90, position: 'insideLeft' }} />
//                   <Tooltip />
//                   <Legend />
//                   <Line type="monotone" dataKey="started" name="Started" stroke="#0088FE" />
//                   <Line type="monotone" dataKey="partial" name="Partially Fulfilled" stroke="#00C49F" />
//                   <Line type="monotone" dataKey="fulfilled" name="Fully Fulfilled" stroke="#FFBB28" />
//                 </LineChart>
//               </ResponsiveContainer>
//             </div>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default OrderFulfillmentDashboard;