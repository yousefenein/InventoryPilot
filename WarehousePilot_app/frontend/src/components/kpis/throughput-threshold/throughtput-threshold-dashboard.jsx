import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import NavBar from "../../navbar/App";
import SideBar from '../../dashboard_sidebar1/App';
import ThroughputBarGraph from './throughput-graph';
import ThroughputDonutChart from './throughput-current-week-donut-chart';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const ThroughputThresholdDashboard = ({ userData }) => {
    const navigate = useNavigate();
    const [isSidebarOpen, setSidebarOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [data, setData] = useState([]); //formatted data for ThroughputBarGraph

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

            // Format data for ThroughputBarGraph
            const formattedData = response.data.map((item) => {
                return {
                    date: item.date,
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

    /* formatDataForDonutChart: format data for ThroughputDonutChart component */
    const formatDataForDonutChart = (data) => {
        return [
            { name: 'Picked', value: data.picked },
            { name: 'Packed', value: data.packed },
            { name: 'Shipped', value: data.shipped }
        ];
    };

    useEffect(() => {
        fetchData();
        if (data.length == 0){ //TODO: Remove this if block after backend is implemented 
            setData([
                { date: '2025-03-10', picked: 400, packed: 300, shipped: 200 },
                { date: '2025-03-11', picked: 500, packed: 400, shipped: 300 },
                { date: '2025-03-12', picked: 600, packed: 500, shipped: 400 },
                { date: '2025-03-13', picked: 700, packed: 600, shipped: 500 },
                { date: '2025-03-14', picked: 600, packed: 500, shipped: 400 },
                { date: '2025-03-15', picked: 700, packed: 600, shipped: 500 },
                { date: '2025-03-16', picked: 400, packed: 300, shipped: 200 },
                { date: '2025-03-17', picked: 500, packed: 400, shipped: 300 },
                { date: '2025-03-18', picked: 600, packed: 500, shipped: 400 },
                { date: '2025-03-19', picked: 700, packed: 600, shipped: 500 },
                { date: '2025-03-20', picked: 600, packed: 500, shipped: 400 },
                { date: '2025-03-21', picked: 700, packed: 600, shipped: 500 },
                { date: '2025-03-22', picked: 400, packed: 300, shipped: 200 },
                { date: '2025-03-23', picked: 500, packed: 400, shipped: 300 },
                { date: '2025-03-24', picked: 600, packed: 500, shipped: 400 },
                { date: '2025-03-25', picked: 700, packed: 600, shipped: 500 },
                { date: '2025-03-26', picked: 600, packed: 500, shipped: 400 },
                { date: '2025-03-27', picked: 700, packed: 600, shipped: 500 },
            ]);
            setDonutChartData(formatDataForDonutChart({ picked: 700, packed: 600, shipped: 500 }));
        }
        else 
            setDonutChartData(formatDataForDonutChart(data[data.length - 1]));
        setLoading(false);
    }, []);

    const handleViewDetails = () => {
        navigate('/kpi');
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <SideBar userData={userData} isOpen={isSidebarOpen} />

            {/* Navbar */}
            <div className="flex-1 sm:ml-10 sm:mt-2">
                <NavBar />
            </div>

            {/* Header - Title and Back to KPI Page button*/}
            <div className="flex justify-between items-center mx-10">
                <h1 className="text-3xl font-bold mb-6">
                    Throughput Threshold Dashboard
                </h1>
                <button
                    className="bg-red-600 text-white py-1 px-3 rounded"
                    onClick={handleViewDetails}  //bg-gray-500 hover
                >
                    Back to KPI Overview
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center items-center h-64 bg-white rounded-lg shadow-sm p-4">
                    <div className="animate-pulse text-gray-600">Loading data...</div>
                </div>
            ) : (
                <>
                    {/* Donut Chart (This Week's Throughput Threshold) and Associated Orders */}
                    <div className="flex flex-row justify-between sm:ml-10 sm:mt-2 mx-10 space-x-4 mb-4">
                        <div className="flex-1">
                            <ThroughputDonutChart data={donutChartData} />
                        </div>
                        <div className="flex-1">
                            <ThroughputTable data={data}/>
                        </div>
                    </div>

                    {/* Week by week throughput data */}
                    <div className="flex-1 sm:ml-10 sm:mt-2 mx-10">
                        <ThroughputBarGraph data={data} loading={loading} title={'Throughput per Week'} />
                    </div>
                </>
            )}
        </div>
    );
}

export default ThroughputThresholdDashboard;