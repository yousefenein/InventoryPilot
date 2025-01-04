import React, { useState, useEffect, useMemo } from 'react';
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
} from '@nextui-org/react';
import { SearchIcon } from '@nextui-org/shared-icons';
import axios from 'axios';
import Sidebar from '../dashboard_sidebar/Sidebar';
import Header from '../dashboard_sidebar/Header';

const OrderListView = () => {
  const [filterValue, setFilterValue] = useState("");
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [userData, setUserData] = useState(null);
  const [updatingOrderId, setUpdatingOrderId] = useState(null); // Track which order is being updated

  const rowsPerPage = 10;

  // Fetch orders function
  const fetchOrders = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authorization token found');
        setLoading(false);
        return;
      }

      const response = await axios.get('http://127.0.0.1:8000/orders/ordersview/', {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

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
      console.error('Error fetching orders:', err);
      setError('Failed to fetch orders');
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchOrders();
  }, []);

  // Handle "Start" action
  const handleStart = async (orderId) => {
    try {
      setUpdatingOrderId(orderId);
      setError(null);
  
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authorization token found');
        return;
      }
  
      const response = await axios.post(`http://127.0.0.1:8000/orders/start_order/${orderId}/`, {}, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
  
      // Check if the response was successful
      if (response.data.status === 'success') {
        // Update the local state immediately
        setRows(prevRows => 
          prevRows.map(row => 
            row.order_id === orderId 
              ? { ...row, status: 'In Progress' }
              : row
          )
        );
      }
    } catch (err) {
      console.error('Error starting the order:', err);
      setError('Error starting the order');
    } finally {
      setUpdatingOrderId(null);
    }
  };

  // Filter rows by search text
  const filteredRows = useMemo(() => {
    if (!filterValue.trim()) return rows;
    const searchTerm = filterValue.toLowerCase();
    return rows.filter((row) => {
      const orderIdMatch = row.order_id?.toString().toLowerCase().includes(searchTerm);
      const durationMatch = row.estimated_duration?.toString().toLowerCase().includes(searchTerm);
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
  }, [page, rowsPerPage, filteredRows]);

  const totalPages = Math.ceil(filteredRows.length / rowsPerPage);

  const toggleSidebar = () => {
    setSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="flex h-full">
      <Sidebar userData={userData} isOpen={isSidebarOpen} />

      <div className="flex-1 sm:ml-64">
        <Header userData={userData} toggleSidebar={toggleSidebar} />

        <div className="mt-16 p-8">
          <h1 className="text-2xl font-bold mb-6">Orders</h1>

          {/* Error message with dismiss button */}
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
              endContent={<SearchIcon className="text-default-400" width={16} />}
              css={{ width: '300px' }}
            />
          </div>

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div>Loading...</div>
            </div>
          ) : (
            <>
              <Table
                aria-label="Order list"
                shadow
                css={{ height: 'auto', minWidth: '100%' }}
              >
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
                      <TableCell>{item.status}</TableCell>
                      <TableCell>{item.due_date}</TableCell>
                      <TableCell>
                        <Button
                          color="primary"
                          size="sm"
                          isLoading={updatingOrderId === item.order_id}
                          isDisabled={item.status === 'In Progress' || updatingOrderId !== null}
                          onPress={() => handleStart(item.order_id)}
                        >
                          {item.status === 'In Progress' ? 'Started' : 'Start'}
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