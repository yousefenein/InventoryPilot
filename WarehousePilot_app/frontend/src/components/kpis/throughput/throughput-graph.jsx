import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardBody } from "@heroui/card";

/* data format for ThroughputBarGraph
const data = [
  { week: 'Week 1', picked: 400, packed: 300, shipped: 200 },
  { week: 'Week 2', picked: 500, packed: 400, shipped: 300 },
  { week: 'Week 3', picked: 600, packed: 500, shipped: 400 },
  { week: 'Week 4', picked: 700, packed: 600, shipped: 500 },
];
*/

export default function ThroughputBarGraph({data}) {
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
            <Bar dataKey="picked" fill="#8884d8" /> {/* Change colors */}
            <Bar dataKey="packed" fill="#82ca9d" />
            <Bar dataKey="shipped" fill="#ffc658" />
          </BarChart>
        </ResponsiveContainer>
      </CardBody>
    </Card>
  );
}
