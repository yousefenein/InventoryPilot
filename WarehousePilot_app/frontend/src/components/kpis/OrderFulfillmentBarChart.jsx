import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const COLORS = ['#4CAF50', '#8BC34A', '#FF9800'];

const OrderFulfillmentBarChart = ({ data }) => {
  // Prepare the chart data
  const prepareChartData = (periodData) => {
    if (!periodData || !Array.isArray(periodData) || periodData.length === 0) {
      return [];
    }

    return periodData.map(period => {
      const startedOrders = period.orders_started || 0;
      const startedOnly = Math.max(
        0,
        startedOrders - (period.partially_fulfilled || 0) - (period.fully_fulfilled || 0)
      );
      const date = new Date(period.period);
      const formattedDate = date.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric'
      });
      
      return {
        name: formattedDate,
        "Fully Fulfilled": period.fully_fulfilled || 0,
        "Partially Fulfilled": period.partially_fulfilled || 0,
        "Started Only": startedOnly,
        totalStarted: startedOrders
      };
    });
  };

  const chartData = prepareChartData(data);

  // If there is only one data point, normalize manually.
  // Otherwise, let Recharts handle it with stackOffset="expand".
  const finalData =
    chartData.length === 1
      ? chartData.map(item => {
          const total = item.totalStarted;
          return {
            ...item,
            "Fully Fulfilled": total ? item["Fully Fulfilled"] / total : 0,
            "Partially Fulfilled": total ? item["Partially Fulfilled"] / total : 0,
            "Started Only": total ? item["Started Only"] / total : 0,
          };
        })
      : chartData;

  const stackProps = chartData.length > 1 ? { stackOffset: "expand" } : {};

  // Custom tooltip (adjusts for normalized vs. raw values)
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const totalStarted = payload[0].payload.totalStarted;
      
      return (
        <div className="bg-white p-2 border border-gray-200 shadow-sm rounded">
          <p className="font-medium">{label}</p>
          {payload.map((entry, index) => {
            // If only one point, convert normalized value back to count
            const actualCount =
              chartData.length === 1 && totalStarted
                ? (entry.value * totalStarted).toFixed(0)
                : entry.value;
            const percent = totalStarted
              ? ((entry.value) * 100).toFixed(1)
              : '0.0';
            
            return (
              <p key={index} style={{ color: entry.color }}>
                {entry.name}: {actualCount} ({percent}%)
              </p>
            );
          })}
          <p className="text-gray-600 text-sm mt-1">
            Total Started: {totalStarted}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm">
      <h3 className="text-lg font-medium mb-4">Order Fulfillment Trend</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={finalData}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            {...stackProps}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="Fully Fulfilled" stackId="a" fill={COLORS[0]} />
            <Bar dataKey="Partially Fulfilled" stackId="a" fill={COLORS[1]} />
            <Bar dataKey="Started Only" stackId="a" fill={COLORS[2]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default OrderFulfillmentBarChart;

