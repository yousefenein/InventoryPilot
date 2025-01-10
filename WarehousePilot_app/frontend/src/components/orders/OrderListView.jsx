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
} from "@nextui-org/react";
import { SearchIcon } from "@nextui-org/shared-icons";
import axios from "axios";
import SideBar from "../dashboard_sidebar1/App";

import { useNavigate } from "react-router-dom";

const OrderListView = () => {
  const [filterValue, setFilterValue] = useState("");
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [page, setPage] = useState(1);
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [userData, setUserData] = useState(null);
  const [updatingOrderId, setUpdatingOrderId] = useState(null);
  const navigate = useNavigate()
  const rowsPerPage = 10;

  // Filter rows by search text
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

  useEffect(() => {
    fetchOrders();
  }, []);

  // Auto-dismiss success message after 3 seconds
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => {
        setSuccess(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const handleStart = async (orderId) => {
    try {
      setUpdatingOrderId(orderId);
      setError(null);
      setSuccess(null); // Reset previous success message

      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authorization token found");
        return;
      }

      const response = await axios.post(
        `http://127.0.0.1:8000/orders/start_order/${orderId}/`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      console.log("Response from backend:", response.data); // Log the response

      // Make sure the correct field name is accessed here
      if (response.data.status === "success") {
        setRows((prevRows) =>
          prevRows.map((row) =>
            row.order_id === orderId
              ? {
                  ...row,
                  status: response.data.order_status,
                  start_timestamp: response.data.start_timestamp,
                }
              : row
          )
        );
        setSuccess(`Order ${orderId} successfully started!`); // Set success message
      }
    } catch (err) {
      console.error("Error starting the order:", err);
      setError("Error starting the order");
    } finally {
      setUpdatingOrderId(null);
    }
  };

  return (
    <div className="flex h-full">
       {/* Sidebar */}
            <SideBar userData={userData} isOpen={isSidebarOpen} />

      <div className="flex-1 sm:ml-8">
        

        <div className="mt-16 p-8">
          <div className="flex flex-row gap-11">
          
          <h1 className="text-2xl font-bold mb-6">Orders</h1>
          <Button
           color="primary"
           variant='flat'
           onClick = { ()=> navigate("/inventory_pick_list")}

           >
            Inventory picklist
          </Button>

          </div>
          

          {/* Success message */}
          {success && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4 flex justify-between items-center">
              <span>{success}</span>
              <button
                onClick={() => setSuccess(null)}
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
