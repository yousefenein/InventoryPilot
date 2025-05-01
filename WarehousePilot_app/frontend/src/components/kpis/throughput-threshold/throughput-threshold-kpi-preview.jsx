import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import ThroughputBarGraph from "./throughput-graph";
import { parseISO, isAfter, subWeeks, subMonths, subYears } from "date-fns";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default function ThroughputThresholdKpiPreview() {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const [data, setData] = useState([]);
    const [filteredData, setFilteredData] = useState([]); // Data filtered by timeline
    const [range, setRange] = useState("Past Week"); // Default timeline range
    const [isStacked, setIsStacked] = useState(false); // Stack the bars or not

    /* Fetch and format data for ThroughputBarGraph */
    const fetchData = async () => {
        try {
            const token = localStorage.getItem("token");
            if (!token) {
                setError("No authorization token found");
                setLoading(false);
                return;
            }

            const response = await axios.get(`${API_BASE_URL}/kpi_dashboard/throughput-threshold/`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
            });
            // console.log("Throughput data:", response.data); // Log the response data

            const formattedData = response.data.map((item) => ({
                date: item.day,
                picked: item.picked,
                packed: item.packed,
                shipped: item.shipped,
            }));

            setData(formattedData);
            setLoading(false);
        } catch (error) {
            setError(error.message);
            setLoading(false);
        }
    };

    /* Filter data based on the selected range */
    const filterDataByRange = (data, range) => {
        const now = new Date();
        const period = range.trim().split(" ")[1].toLowerCase(); // Extract "week", "month", or "year"

        let startDate;
        if (period === "week") {
            startDate = subWeeks(now, 1);
            setIsStacked(false);
        } else if (period === "month") {
            startDate = subMonths(now, 1);
            setIsStacked(true);
        } else if (period === "year") {
            startDate = subYears(now, 1);
            setIsStacked(true);
        } else {
            throw new Error("Invalid range. Use 'week', 'month', or 'year'.");
        }

        // Filter the data by comparing parsed dates
        return data.filter((item) => {
            const itemDate = parseISO(item.date); // Parse the string date into a Date object
            return itemDate >= startDate && itemDate <= now; // Check if the date is within the range
        });
    };

    /* useEffect - Fetch data on loading component */
    useEffect(() => {
        fetchData();
    }, []);

    // useEffect - Filter data whenever `data` or `range` changes
    useEffect(() => {
        if (data.length > 0) {
            const filtered = filterDataByRange(data, range);
            setFilteredData(filtered);
        }
    }, [data, range]);

    const handleViewDetails = () => {
        navigate("/throughput-threshold");
    };

    const handleRangeClick = (range) => {
        setRange(range);
    };

    return (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
            {/* Header and View Details button */}
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-black dark:text-white">Throughput Threshold</h2>
                <button
                    onClick={handleViewDetails}
                    className="bg-gray-500 dark:bg-gray-700 hover:bg-red-600 dark:hover:bg-red-700 text-white py-1 px-3 rounded transition-colors"
                >
                    View Details
                </button>
            </div>
    
            {/* Timeline Range Selector */}
            <div className="flex space-x-2 mb-4">
                {["Past Week", "Past Month", "Past Year"].map((label) => (
                    <button
                        key={label}
                        onClick={() => handleRangeClick(label)}
                        className={`px-4 py-2 rounded transition-colors ${
                            range === label
                                ? "bg-red-600 dark:bg-red-700 text-white"
                                : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                        }`}
                    >
                        {label}
                    </button>
                ))}
            </div>
    
            {loading ? (
                <div className="text-center dark:text-gray-400">Loading...</div>
            ) : (
                <ThroughputBarGraph data={filteredData} loading={loading} isStacked={isStacked} />
            )}
        </div>
    );
}