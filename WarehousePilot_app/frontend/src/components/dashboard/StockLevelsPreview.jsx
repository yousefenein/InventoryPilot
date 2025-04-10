import { useEffect, useState, useMemo } from 'react';
import { Table, TableHeader, TableBody, TableColumn, TableRow, TableCell, Pagination } from "@heroui/react";
import { Box, Typography, CircularProgress } from '@mui/material'; // Keep other UI components from MUI

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const columns = [
  "SKU Color ID", 
  "Quantity", 
  "Warehouse Number"
];

const StockLevelsPreview = () => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true); // Loading state
  const [error, setError] = useState(null);  // Error handling
  const [page, setPage] = useState(1); // Pagination state

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Authorization token is missing');
      setLoading(false);
      return;
    }

    // Fetch inventory data from the backend
    fetch(`${API_BASE_URL}/inventory/inventorypreview/`, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })
    .then(response => response.json())
    .then(data => {
      if (Array.isArray(data)) {
        // Ensure rows have a unique id using inventory_id, but don't display it
        setRows(data.map(part => ({
          key: part.inventory_id,  // Unique key for each row (required by Table)
          sku_color_id: part.sku_color_id,
          qty: part.qty,
          warehouse_number: part.warehouse_number,
        })));
      } else {
        setError('Failed to fetch valid data');
      }
      setLoading(false);
    })
    .catch(error => {
      console.error('Failed to fetch inventory data:', error);
      setError('Failed to load data');
      setLoading(false);
    });
  }, []);

  // Pagination logic
  const rowsPerPage = 9;
  const paginatedRows = useMemo(() => {
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    return rows.slice(start, end);
  }, [page, rows]);

  const totalPages = Math.ceil(rows.length / rowsPerPage);

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
      <Box mt={10} display="flex" flexDirection="column" alignItems="center">
        <Typography variant="h6" className="dark:text-white">
          Inventory Overview
        </Typography>
        {loading ? (
          <CircularProgress />
        ) : error ? (
          <Typography variant="body1" color="error" className="dark:text-red-500">{error}</Typography>
        ) : (
          <>
            <Table aria-label="Stock Levels Table" className="w-full">
              <TableHeader>
                {columns.map((column, index) => (
                  <TableColumn key={index} className="dark:text-white">{column}</TableColumn>
                ))}
              </TableHeader>
              <TableBody items={paginatedRows}>
                {(item) => (
                  <TableRow key={item.key}>
                    <TableCell className="dark:text-gray-300">{item.sku_color_id}</TableCell>
                    <TableCell className="dark:text-gray-300">{item.qty}</TableCell>
                    <TableCell className="dark:text-gray-300">{item.warehouse_number}</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>

            {/* Pagination */}
            {totalPages > 0 && (
              <div className="flex w-full justify-center mt-4">
                <Pagination
                  total={totalPages}
                  initialPage={1}
                  current={page}
                  onChange={(newPage) => setPage(newPage)}
                  classNames={{
                    item: "bg-white text-black dark:bg-gray-700 dark:text-white",
                    cursor: "bg-black text-white dark:bg-blue-600 dark:text-white",
                  }}
                />
              </div>
            )}
          </>
        )}
      </Box>
    </div>
  );
};

export default StockLevelsPreview;


