import React from 'react';

const OrderFulfillmentTable = ({ currentPeriod }) => {
  if (!currentPeriod) return null;

  const total = currentPeriod.total_orders || 1; // Avoid division by zero
  const tableData = [
    { name: 'Started', value: currentPeriod.orders_started || 0, percent: ((currentPeriod.orders_started / total) * 100).toFixed(1) },
    { name: 'Partially Fulfilled', value: currentPeriod.partially_fulfilled || 0, percent: ((currentPeriod.partially_fulfilled / total) * 100).toFixed(1) },
    { name: 'Fully Fulfilled', value: currentPeriod.fully_fulfilled || 0, percent: ((currentPeriod.fully_fulfilled / total) * 100).toFixed(1) },
    { 
      name: 'Not Started', 
      value: Math.max(0, total - (currentPeriod.orders_started || 0) - (currentPeriod.partially_fulfilled || 0) - (currentPeriod.fully_fulfilled || 0)),
      percent: ((Math.max(0, total - (currentPeriod.orders_started || 0) - (currentPeriod.partially_fulfilled || 0) - (currentPeriod.fully_fulfilled || 0)) / total) * 100).toFixed(1)
    }
  ];

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm">
      <h3 className="text-lg font-medium mb-4">Order Fulfillment Data</h3>
      <table className="w-full border-collapse border border-gray-300">
        <thead>
          <tr className="bg-gray-100">
            <th className="border px-4 py-2">Metric</th>
            <th className="border px-4 py-2">Value</th>
            <th className="border px-4 py-2">Percentage</th>
          </tr>
        </thead>
        <tbody>
          {tableData.map((entry, index) => (
            <tr key={index}>
              <td className="border px-4 py-2">{entry.name}</td>
              <td className="border px-4 py-2">{entry.value}</td>
              <td className="border px-4 py-2">{entry.percent}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default OrderFulfillmentTable;
