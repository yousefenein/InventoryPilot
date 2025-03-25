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

    const COLORS = ['#FF6B6B', '#FFA94D', '#FFD66B'];

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
                    week: item.date,
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

    if (data.length == 0) { // TODO: Remove this when API is ready
        setData([
            { week: 'Week 1', picked: 400, packed: 300, shipped: 200 },
            { week: 'Week 2', picked: 500, packed: 400, shipped: 300 },
            { week: 'Week 3', picked: 600, packed: 500, shipped: 400 },
            { week: 'Week 4', picked: 700, packed: 600, shipped: 500 },
            { week: 'Week 5', picked: 600, packed: 500, shipped: 400 },
            { week: 'Week 6', picked: 700, packed: 600, shipped: 500 },
            { week: 'Week 7', picked: 400, packed: 300, shipped: 200 },
            { week: 'Week 8', picked: 500, packed: 400, shipped: 300 },
            { week: 'Week 9', picked: 600, packed: 500, shipped: 400 },
            { week: 'Week 10', picked: 700, packed: 600, shipped: 500 },
            { week: 'Week 11', picked: 600, packed: 500, shipped: 400 },
            { week: 'Week 12', picked: 700, packed: 600, shipped: 500 },
            { week: 'Week 13', picked: 400, packed: 300, shipped: 200 },
            { week: 'Week 14', picked: 500, packed: 400, shipped: 300 },
            { week: 'Week 15', picked: 600, packed: 500, shipped: 400 },
            { week: 'Week 16', picked: 700, packed: 600, shipped: 500 },
            { week: 'Week 17', picked: 600, packed: 500, shipped: 400 },
            { week: 'Week 18', picked: 700, packed: 600, shipped: 500 },
        ]);
        setLoading(false);
    }

    const currentWeekThreshold = [
        { name: 'Picked', value: data[data.length - 1].picked },
        { name: 'Packed', value: data[data.length - 1].packed },
        { name: 'Shipped', value: data[data.length - 1].shipped }
    ];


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
                    <div className="flex-1 sm:ml-10 sm:mt-2 mx-10">
                        <ThroughputDonutChart data={currentWeekThreshold} />
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