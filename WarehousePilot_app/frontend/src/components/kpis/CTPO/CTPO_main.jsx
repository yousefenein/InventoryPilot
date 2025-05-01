// CTPO: Cycle Time Per Order
// This page displays more in-depth information about cycle time per order

import React, { useState, useEffect, useMemo } from "react";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Input,
  Pagination,
  Button,
  Popover,
  PopoverTrigger,
  PopoverContent,
  Badge,
} from "@heroui/react";
import { SearchIcon } from "@heroui/shared-icons";
import { Icon } from "@iconify/react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import SideBar from "../../dashboard_sidebar1/App";
import NavBar from "../../navbar/App";
import ProgressBar from "./progressbar";
import DelayedOrdersNotifCard from "./DelayedOrderAlerts/App"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const CTPO = () => {

  const [filterValue, setFilterValue] = useState("");
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const navigate = useNavigate();
  const [isDarkMode, setIsDarkMode] = useState(false);

  const rowsPerPage = 8;

  const [unreadNotifications, setUnreadNotifications] = useState(() => {
    const savedStatus = localStorage.getItem("unreadNotifications");
    return savedStatus ? JSON.parse(savedStatus) : true;
  });

  // Filter rows by search text
  const filteredRows = useMemo(() => {
    if (!filterValue.trim()) return rows;
    const searchTerm = filterValue.toLowerCase();
    return rows.filter((row) => {
      const orderIdMatch = row.order_id
        ?.toString()
        .toLowerCase()
        .includes(searchTerm);
      const statusMatch = row.status?.toLowerCase().includes(searchTerm);
      return orderIdMatch || statusMatch;
    });
  }, [rows, filterValue]);

  // Apply pagination
  const paginatedRows = useMemo(() => {
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    return filteredRows.slice(start, end);
  }, [page, filteredRows]);

  // Calculate total pages
  const totalPages = Math.ceil(filteredRows.length / rowsPerPage);

  const fetchOrders = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authorization token found");
        setLoading(false);
        return;
      }

      const response = await axios.get(
        `${API_BASE_URL}/orders/cycle_time_per_order/`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      // Filter response data to only include items with a status
      const filteredData = response.data.filter(row => row.status !== null);
      console.log("filteredData", filteredData);

      setRows(
        filteredData.map((row, index) => ({
          id: index + 1,
          order_id: row.order_id,
          status: row.status,
          cycle_time: row.cycle_time,
          pick_time: row.pick_time,
          pack_time: row.pack_time,
          ship_time: row.ship_time,
        }))
      );
      setLoading(false);
    } catch (err) {
      console.error("Error fetching orderes:", err);
      setError("Failed to fetch orders");
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  useEffect(() => {
    // Check for dark mode class on the HTML element
    const htmlElement = document.documentElement;
    setIsDarkMode(htmlElement.classList.contains('dark'));

    // Set up a mutation observer to watch for class changes
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'class') {
          setIsDarkMode(htmlElement.classList.contains('dark'));
        }
      });
    });

    observer.observe(htmlElement, {
      attributes: true,
      attributeFilter: ['class']
    });

    return () => observer.disconnect();
  }, []);


  const handleViewOrderDetails = (order_id) => {
    navigate(`/manufacturing_list_item/${order_id}`);
  };

  const handleNotificationsRead = () => {
    setUnreadNotifications(false);
    localStorage.setItem("unreadNotifications", JSON.stringify(false)); // Save to local storage
  };

  const CTPO_COLUMNS = ["Order ID", "Status", "Cycle Time"];

  const COLORS = isDarkMode ? ["#8884d8", "#ff4444"] : ["#8B0000", "#A52A2A"];

  const handleViewDetails = () => {
    navigate('/kpi');
  };
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">

      <SideBar />
      <div className="flex-1">
        <NavBar />
        <main className="max-w-screen mx-auto p-10">

          <div className="flex justify-between items-center mb-4">
            <h1 className="text-3xl font-bold mb-6 dark:text-white ">Cycle Time Per Order Statistics</h1>
            <button
              className={`${isDarkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-red-600'} text-white py-1 px-3 rounded`}
              onClick={handleViewDetails}
            >
              Back to KPI Overview
            </button>
          </div>
          {/* Error message */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
              {error}
            </div>
          )}

          <div className="flex justify-between items-center mb-5">
            {/* Search Input */}
            <div className="flex items-center gap-2">
              <Input
                size="md"
                placeholder="Search orders"
                value={filterValue}
                onChange={(e) => setFilterValue(e.target.value)}
                endContent={<SearchIcon className="text-default-400" width={16} />}
                className="w-72"
              />
            </div>

            {/* Delayed Orders Notifications */}
            <div className="flex items-center gap-6">
              <Popover>
                <PopoverTrigger>
                  <Button isIconOnly variant="flat">
                    <Badge
                      style={{ backgroundColor: "#b91c1c" }} // Custom red color
                      content=" "
                      shape="circle"
                      isInvisible={!unreadNotifications}
                    >
                      <Icon icon="solar:bell-outline" width={24} />
                    </Badge>
                  </Button>
                </PopoverTrigger>
                <PopoverContent>
                  <DelayedOrdersNotifCard onMarkAllAsRead={handleNotificationsRead} />
                </PopoverContent>
              </Popover>
            </div>
          </div>

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div>Loading...</div>
            </div>
          ) : (
            <>
              <Table aria-label="CTPO" className="min-w-full w-full"


                classNames={{
                  wrapper: "dark:bg-gray-800",
                  th: "dark:bg-gray-700 dark:text-white",
                  tr: "dark:hover:bg-gray-700",
                  td: "dark:text-white dark:before:bg-transparent"
                }}
              >
                <TableHeader>
                  {CTPO_COLUMNS.map((column) => (
                    <TableColumn key={column}>{column}</TableColumn>
                  ))}
                </TableHeader>

                <TableBody items={paginatedRows}>
                  {(item) => (
                    <TableRow key={item.id}>
                      <TableCell>{item.order_id}</TableCell>
                      <TableCell>{item.status ? item.status : "N/A"}</TableCell>
                      <TableCell><ProgressBar
                        pickTime={item.pick_time}
                        packTime={item.pack_time}
                        shipTime={item.ship_time} />
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>

              {/* Pagination*/}
              <div className="flex justify-between items-center mt-4">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Page {page} of {totalPages}
                </span>
                <Pagination
                  total={totalPages}
                  initialPage={1}
                  current={page}
                  onChange={(newPage) => { setPage(newPage) }}
                  className="text-gray-600 dark:text-gray-400"
                  classNames={{
                    item: "dark:bg-gray-700 dark:text-white",
                    cursor: "bg-black text-white dark:bg-black dark:text-white"
                  }}
                />
              </div>
            </>
          )}

        </main>

      </div>
    </div>
  );
};

export default CTPO;