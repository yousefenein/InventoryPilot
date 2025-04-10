import { useEffect, useState, useMemo } from 'react';
import { Table, TableHeader, TableBody, TableColumn, TableRow, TableCell, Pagination } from "@heroui/react";
import { Box, Typography, CircularProgress, TextField } from '@mui/material';
import { useNavigate } from "react-router-dom";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const columns = [
  "SKU Color ID", 
  "Quantity", 
  "Warehouse Number"
];

const StockLevelsPreview = () => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Authorization token is missing');
      setLoading(false);
      return;
    }

    fetch(`${API_BASE_URL}/inventory/inventorypreview/`, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })
    .then(response => response.json())
    .then(data => {
      if (Array.isArray(data)) {
        setRows(data.map(part => ({
          key: part.inventory_id,
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

  const filteredRows = useMemo(() => {
    return rows.filter(row =>
      row.sku_color_id.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [searchTerm, rows]);

  const rowsPerPage = 9;
  const paginatedRows = useMemo(() => {
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    return filteredRows.slice(start, end);
  }, [page, filteredRows]);

  const totalPages = Math.ceil(filteredRows.length / rowsPerPage);

  const handleDetailsClick = () => {
    navigate("/inventory-stock"); // Navigate to the full inventory page
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
      {/* Header row with title and details button */}
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-xl font-semibold dark:text-white">Inventory Overview</h2>
        <button
          onClick={handleDetailsClick}
          className="bg-gray-500 dark:bg-gray-700 hover:bg-red-600 dark:hover:bg-red-700 text-white py-1 px-3 rounded transition-colors"
        >
          View Details
        </button>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <TextField
          label="Search by SKU Color ID"
          variant="outlined"
          size="small"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ 
            width: '300px',
            '& .MuiOutlinedInput-root': {
              borderRadius: '24px',
            }
          }}
        />
      </div>

      {loading ? (
        <div className="flex justify-center w-full">
          <CircularProgress />
        </div>
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
    </div>
  );
};

export default StockLevelsPreview;




