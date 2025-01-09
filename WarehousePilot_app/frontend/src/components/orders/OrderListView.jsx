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
} from "@nextui-org/react"; // Importing necessary components from NextUI for the table and buttons
import { SearchIcon } from "@nextui-org/shared-icons"; // Importing SearchIcon from NextUI shared icons
import axios from "axios"; // Importing Axios for making HTTP requests
import Sidebar from "../dashboard_sidebar/Sidebar"; // Importing Sidebar component
import Header from "../dashboard_sidebar/Header";
import { useNavigate } from "react-router-dom"; // Importing Header component

const OrderListView = () => {
  // State variables
  const [filterValue, setFilterValue] = useState(""); // Filter value for search functionality
  const [rows, setRows] = useState([]); // To store the list of orders fetched from the backend
  const [loading, setLoading] = useState(true); // To manage loading state
  const [error, setError] = useState(null); // To store any error message
  const [successOrderStart, setSuccessOrderStart] = useState(null); // Success message for starting the order
  const [successListGeneration, setSuccessListGeneration] = useState(null); // Success message for list generation
  const [page, setPage] = useState(1); // Page number for pagination
  const [isSidebarOpen, setSidebarOpen] = useState(false); // To toggle the sidebar visibility
  const [userData, setUserData] = useState(null); // To store user data
  const [updatingOrderId, setUpdatingOrderId] = useState(null); // To track which order is being updated
  const navigate = useNavigate()
  const rowsPerPage = 10; // Number of rows to display per page

  // Filter rows based on search text (order ID, duration, status, due date)
  const filteredRows = useMemo(() => {
    if (!filterValue.trim()) return rows;
    const searchTerm = filterValue.toLowerCase();
    return rows.filter((row) => {
      const orderIdMatch = row.order_id
        ?.toString()
        .toLowerCase()
        .includes(searchTerm);
      const durationMatch = row.estimated_duration
        ?.toString()
        .toLowerCase()
        .includes(searchTerm);
      const statusMatch = row.status?.toLowerCase().includes(searchTerm);
      const dueDateMatch = row.due_date?.toLowerCase().includes(searchTerm);
      return orderIdMatch || durationMatch || statusMatch || dueDateMatch;
    });
  }, [rows, filterValue]);

  // Apply pagination to the filtered rows
  const paginatedRows = useMemo(() => {
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    return filteredRows.slice(start, end);
  }, [page, filteredRows]);

  // Calculate total pages based on the number of filtered rows
  const totalPages = Math.ceil(filteredRows.length / rowsPerPage);

  // Fetch orders data from the backend
  const fetchOrders = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authorization token found");
        setLoading(false);
        return;
      }

      const response = await axios.get(
        "http://127.0.0.1:8000/orders/ordersview/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      setRows(
        response.data.map((row, index) => ({
          id: index + 1,
          order_id: row.order_id,
          estimated_duration: row.estimated_duration,
          status: row.status,
          due_date: row.due_date,
        }))
      );
      setLoading(false);
    } catch (err) {
      console.error("Error fetching orders:", err);
      setError("Failed to fetch orders");
      setLoading(false);
    }
  };

  // Fetch orders on component mount
  useEffect(() => {
    fetchOrders();
  }, []);

  // Auto-dismiss success message for starting the order after 3 seconds
  useEffect(() => {
    if (successOrderStart) {
      const timer = setTimeout(() => {
        setSuccessOrderStart(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [successOrderStart]);

  // Auto-dismiss success message for generating lists after 3 seconds
  useEffect(() => {
    if (successListGeneration) {
      const timer = setTimeout(() => {
        setSuccessListGeneration(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [successListGeneration]);

  // Handle the start button click event
  const handleStart = async (orderId) => {
    try {
      setUpdatingOrderId(orderId);
      setError(null);
      setSuccessOrderStart(null); // Reset previous success message
  
      const token = localStorage.getItem('token');
      if (!token) {
        setError("No authorization token found");
        return;
      }
  
      // Send POST request to start the order
      const response = await axios.post(`http://127.0.0.1:8000/orders/start_order/${orderId}/`, {}, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
  
      console.log('Response from backend (start_order):', response.data); // Log the response
  
      if (response.data.status === 'success') {
        // Update the order status and start timestamp
        setRows(prevRows => 
          prevRows.map(row => 
            row.order_id === orderId 
              ? { ...row, status: response.data.order_status, start_timestamp: response.data.start_timestamp }
              : row
          )
        );
        setSuccessOrderStart(`Order ${orderId} successfully started!`); // Set success message for starting the order
  
        // Second POST request to generate the list (after starting the order)
        const generateListsResponse = await axios.post(
          'http://127.0.0.1:8000/orders/generateLists/', 
          { orderID: orderId }, // Send the orderId in the body
          { 
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            }
          }
        );
        
        console.log('Response from backend (generateLists):', generateListsResponse.data);
  
        if (generateListsResponse.data.detail) {
          setSuccessListGeneration(generateListsResponse.data.detail); // Set the success message from the backend
        }
      } else {
        setError(`Error: ${response.data.message}`); // Display specific error message from backend if available
      }
    } catch (err) {
      console.error('Error starting the order:', err);
      // Check for specific error response from backend if available
      if (err.response) {
        setError(`Error: ${err.response.data.message || 'Unknown error occurred'}`);
      } else {
        setError('Error starting the order');
      }
    } finally {
      setUpdatingOrderId(null);
    }
  };

  return (
    <div className="flex h-full">
      <Sidebar userData={userData} isOpen={isSidebarOpen} />

      <div className="flex-1 sm:ml-64">
        <Header
          userData={userData}
          toggleSidebar={() => setSidebarOpen(!isSidebarOpen)}
        />

        <div className="mt-16 p-8">
          <div className="flex flex-row gap-11">
          
          <h1 className="text-2xl font-bold mb-6">Orders</h1>

          {/* Success message for starting the order */}
          {successOrderStart && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4 flex justify-between items-center">
              <span>{successOrderStart}</span>
              <button
                onClick={() => setSuccessOrderStart(null)}
                className="bg-transparent text-green-700 hover:text-green-900 font-semibold px-2"
              >
                ×
              </button>
            </div>
          )}

          {/* Success message for generating the lists */}
          {successListGeneration && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4 flex justify-between items-center">
              <span>{successListGeneration}</span>
              <button
                onClick={() => setSuccessListGeneration(null)}
                className="bg-transparent text-green-700 hover:text-green-900 font-semibold px-2"
              >
                ×
              </button>
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4 flex justify-between items-center">
              <span>{error}</span>
              <button
                onClick={() => setError(null)}
                className="bg-transparent text-red-700 hover:text-red-900 font-semibold px-2"
              >
                ×
              </button>
            </div>
          )}

          {/* Search Input */}
          <div className="mb-6 flex items-center gap-2">
            <Input
              size="md"
              placeholder="Search orders"
              value={filterValue}
              onChange={(e) => setFilterValue(e.target.value)}
              endContent={
                <SearchIcon className="text-default-400" width={16} />
              }
              className="w-72"
            />
          </div>

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div>Loading...</div>
            </div>
          ) : (
            <>
              <Table aria-label="Order list" className="min-w-full">
                <TableHeader>
                  <TableColumn>Order ID</TableColumn>
                  <TableColumn>Estimated Duration</TableColumn>
                  <TableColumn>Status</TableColumn>
                  <TableColumn>Due Date</TableColumn>
                  <TableColumn>Action</TableColumn>
                </TableHeader>

                <TableBody items={paginatedRows}>
                  {(item) => (
                    <TableRow key={item.id}>
                      <TableCell>{item.order_id}</TableCell>
                      <TableCell>{item.estimated_duration}</TableCell>
                      <TableCell>
                        <span
                          className={`px-2 py-1 rounded ${
                            item.status === "In Progress"
                              ? "bg-blue-100 text-blue-800"
                              : ""
                          }`}
                        >
                          {item.status}
                        </span>
                      </TableCell>
                      <TableCell>{item.due_date}</TableCell>
                      <TableCell>
                        <Button
                          color={
                            item.status === "In Progress"
                              ? "success"
                              : "primary"
                          }
                          size="sm"
                          isLoading={updatingOrderId === item.order_id}
                          isDisabled={
                            item.status === "In Progress" ||
                            updatingOrderId !== null
                          }
                          onPress={() => handleStart(item.order_id)}
                        >
                          {item.status === "In Progress" ? "Started" : "Start"}
                        </Button>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>

              <div className="flex justify-between items-center mt-4">
                <span>
                  Page {page} of {totalPages}
                </span>
                <Pagination
                  total={totalPages}
                  initialPage={1}
                  current={page}
                  onChange={(newPage) => setPage(newPage)}
                />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default OrderListView;

