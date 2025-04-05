import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import NavBar from "../../navbar/App";
import SideBar from '../../dashboard_sidebar1/App';
import ThroughputBarGraph from './throughput-graph';
import ThroughputDonutChart from './throughput-current-week-donut-chart';
import ThroughputTable from './throughput-table';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const ThroughputThresholdDashboard = ({ userData }) => {
    const navigate = useNavigate();
    const [isSidebarOpen, setSidebarOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [data, setData] = useState([]); //formatted data for ThroughputBarGraph
    const [donutChartData, setDonutChartData] = useState([]); //formatted data for ThroughputDonutChart

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
                `${API_BASE_URL}/kpi_dashboard/throughput-threshold/`, //TODO: Change this to throughput path
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
                    date: item.day,
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

    /* useEffect - fetch data and set loading state */
    useEffect(() => {
        fetchData();
        setLoading(false);
    }, []);

    // Had to separate this useEffect from the one above to avoid async issues
    useEffect(() => {
        if (data.length > 0) {
            setDonutChartData(formatDataForDonutChart(data[data.length - 1]));
        }
    }, [data]); // Run this effect whenever `data` changes

    /* handleViewDetails: navigate to KPI page */
    const handleViewDetails = () => {
        navigate('/kpi');
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <SideBar userData={userData} isOpen={isSidebarOpen} />

            {/* Navbar */}
            <div className="flex-1 sm:ml-10 sm:mt-2">
                <NavBar />
            </div>

            {/* Header - Title and Back to KPI Page button*/}
            <div className="flex justify-between items-center mx-10">
                <h1 className="text-3xl font-bold mb-6 dark:text-white">
                    Throughput Threshold Dashboard
                </h1>
                <button
                    className="bg-red-600 dark:bg-red-700 text-white py-1 px-3 rounded hover:bg-red-700 dark:hover:bg-red-800 transition-colors"
                    onClick={handleViewDetails}
                >
                    Back to KPI Overview
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center items-center h-64 bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
                    <div className="animate-pulse text-gray-600 dark:text-gray-400">Loading data...</div>
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
                        <ThroughputBarGraph 
                            data={data} 
                            loading={loading} 
                            title={'Throughput per Week'} 
                            isStacked={true} 
                            darkMode={true} // Make sure your ThroughputBarGraph component supports dark mode
                        />
                    </div>
                </>
            )}
        </div>
    );
}

export default ThroughputThresholdDashboard;