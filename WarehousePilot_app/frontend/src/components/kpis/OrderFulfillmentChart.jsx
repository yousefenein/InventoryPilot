import React from 'react';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, 
  Tooltip, Legend
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const OrderFulfillmentChart = ({ currentPeriod }) => {
  // Function to prepare data for the donut chart
  const prepareChartData = (periodData) => {
    if (!periodData) return [];
    const total = periodData.total_orders || 1; // Avoid division by zero

    return [
      { 
        name: 'Fully Fulfilled', 
        value: periodData.fully_fulfilled || 0, 
        percent: ((periodData.fully_fulfilled / total) * 100).toFixed(1),
        count: periodData.fully_fulfilled || 0
      },
      { 
        name: 'Partially Fulfilled', 
        value: periodData.partially_fulfilled || 0, 
        percent: ((periodData.partially_fulfilled / total) * 100).toFixed(1),
        count: periodData.partially_fulfilled || 0
      },
      { 
        name: 'Started Only', 
        value: Math.max(0, (periodData.orders_started || 0) - (periodData.partially_fulfilled || 0) - (periodData.fully_fulfilled || 0)),
        percent: ((Math.max(0, (periodData.orders_started || 0) - (periodData.partially_fulfilled || 0) - (periodData.fully_fulfilled || 0)) / total) * 100).toFixed(1),
        count: Math.max(0, (periodData.orders_started || 0) - (periodData.partially_fulfilled || 0) - (periodData.fully_fulfilled || 0))
      },
      { 
        name: 'Not Started', 
        value: Math.max(0, total - (periodData.orders_started || 0)),
        percent: ((Math.max(0, total - (periodData.orders_started || 0)) / total) * 100).toFixed(1),
        count: Math.max(0, total - (periodData.orders_started || 0))
      }
    ];
  };

  // Custom tooltip to display both percentage and count
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-2 border border-gray-200 shadow-sm rounded">
          <p className="font-medium">{payload[0].payload.name}</p>
          <p>Count: {payload[0].payload.count}</p>
          <p>Percentage: {payload[0].payload.percent}%</p>
        </div>
      );
    }
    return null;
  };

  // Custom label to display name and percentage
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index, name }) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.6;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    const chartData = prepareChartData(currentPeriod);
    // Only show label if percentage is significant enough (>5%)
    if (parseFloat(chartData[index].percent) < 5) return null;

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor="middle" 
        dominantBaseline="central"
        fontSize={12}
        fontWeight="bold"
      >
        {`${chartData[index].percent}%`}
      </text>
    );
  };

  const chartData = prepareChartData(currentPeriod);

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm">
      <h3 className="text-lg font-medium mb-4">Order Fulfillment Status: {currentPeriod?.period}</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie 
              data={chartData} 
              cx="50%" 
              cy="50%" 
              innerRadius={70} 
              outerRadius={130} 
              fill="#8884d8" 
              dataKey="value"
              labelLine={false}
              label={renderCustomizedLabel}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              layout="vertical" 
              verticalAlign="middle" 
              align="right"
              formatter={(value, entry, index) => {
                return (
                  <span className="text-sm">
                    {value}: {chartData[index].percent}%
                  </span>
                );
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default OrderFulfillmentChart;