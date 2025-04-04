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
  Checkbox,
} from "@heroui/react";
import { SearchIcon } from "@heroui/shared-icons";
import { Spinner } from "@heroui/spinner";
import axios from "axios";
import SideBar from "../dashboard_sidebar1/App";

import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
import NavBar from "../navbar/App";
import { useNavigate } from "react-router-dom";
import { time } from "framer-motion";
dayjs.extend(utc);
dayjs.extend(timezone);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function InventoryPickingLogs() {
  const [rows, setRows] = useState([]); // Data formatted for the table
  const [warehouseFilter, setWarehouseFilter] = useState("");
  const [employeeFilter, setEmployeeFilter] = useState("");
  const navigate = useNavigate();
  const [orderFilter, setOrderFilter] = useState("");
  const [filterValue, setFilterValue] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);

  /* Filter rows based on search text */
  const filteredRows = useMemo(() => {
    if (!filterValue.trim()) return rows;

    const searchTerm = filterValue.toLowerCase();

    return rows.filter((row) => {
      const warehouseMatch = row.warehouse?.toString().includes(searchTerm);
      const employeeMatch = row.employee_id?.toString().includes(searchTerm);
      const orderNumberMatch = row.order_number?.toString().includes(searchTerm);
      return warehouseMatch || employeeMatch || orderNumberMatch;
    });
  }, [rows, filterValue]);

  /* Pagination */
  const rowsPerPage = 12;
  const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
  const paginatedRows = useMemo(() => {
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    return filteredRows.slice(start, end);
  }, [page, filteredRows]);

  const columnHeaders = ["Warehouse", "Date", "Time", "Employee ID", "Transaction Type", "Order #", "SKU #", "Location", "Qty Out"];


  /* fetchData: getting employee picking data from packing and formatting data for table */
  const fetchData = async () => {
    try {
      // Get authorization token
      const token = localStorage.getItem("token");

      // Fetch data from the API
      if (!token) {
        setError("No authorization token found");
        setLoading(false);
        return;
      }

      const response = await axios.get(
        `${API_BASE_URL}/picking_logs/`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );


      // Format data for the table
      setRows(
        response.data.map((row, index) => ({
          key: index + 1,
          warehouse: row.warehouse,
          date: dayjs(row.date).format("DD/MM/YYYY"),
          time: dayjs(row.time).format("DD/MM/YYYY HH:mm"),
          employee_id: row.employee_id,
          transaction_type: row.transaction_type,
          order_number: row.order_number,
          sku_color: row.sku_color,
          location: row.location,
          quantity_out: row.qty_out,
        }))
      );
      setLoading(false);
    }
    catch (error) {
      console.error("Error fetching employee picking data:", error);
      setError("Failed to fetch employee picking data");
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="fixed inset-0 bg-white dark:bg-gray-900 overflow-auto" >
      <SideBar />
      <NavBar />
      <div className="flex-1 mt-2 dark:bg-gray-900" >
        <div className="flex-1">
          <div className="px-10 pt-8">
            <div className="flex flex-col gap-4">
              <h1 className="text-2xl font-bold mb-6 dark:text-white">Inventory Picking Logs</h1>

              {/* Error message */}
              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
                  {error}
                </div>
              )}

              <div className="flex items-center gap-2 mb-5">
                <Input
                  size="md"
                  placeholder="Search by warehouse, employee ID, or order #"
                  value={filterValue}
                  onChange={(e) => setFilterValue(e.target.value)}
                  endContent={<SearchIcon className="text-default-400" width={16} />}
                  className="w-1/5"
                />

              </div>

              {loading ? (
                <div className="flex justify-center items-center h-64 dark:text-white">
                  Loading...
                  <Spinner size="lg" color="default" className="ms-5" />
                </div>
              ) : (
                <>
                  {/* Table */}
                  <Table
                    aria-label="Inventory picking logs table"
                    className="min-w-full dark:bg-transparent"
                    classNames={{
                      wrapper: "dark:bg-gray-800 ",
                      th: "dark:bg-gray-700 dark:text-white text-center",
                      tr: "dark:hover:bg-gray-700",
                      td: "dark:text-white dark:before:bg-transparent text-center"
                    }}
                  >

                    <TableHeader>
                      {columnHeaders.map((column) => (
                        <TableColumn key={column} className="dark:text-white text-lg">{column}</TableColumn>
                      ))}
                    </TableHeader>

                    {/* Populate table */}
                    <TableBody items={paginatedRows}>
                      {(item) => (
                        <TableRow key={item.key}>
                          <TableCell>{item.warehouse}</TableCell>
                          <TableCell>{item.date}</TableCell>
                          <TableCell>{item.time}</TableCell>
                          <TableCell>{item.employee_id}</TableCell>
                          <TableCell>{item.transaction_type}</TableCell>
                          <TableCell>{item.order_number}</TableCell>
                          <TableCell>{item.sku_color}</TableCell>
                          <TableCell>{item.location}</TableCell>
                          <TableCell>{item.quantity_out}</TableCell>
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
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InventoryPickingLogs