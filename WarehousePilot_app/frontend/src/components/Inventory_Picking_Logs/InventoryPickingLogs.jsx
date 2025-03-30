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
  const [pickingData, setPickingData] = useState([]); // Data retrieved from the API
  const [rows, setRows] = useState([]); // Data formatted for the table
  const [warehouseFilter, setWarehouseFilter] = useState("");
  const [employeeFilter, setEmployeeFilter] = useState("");
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [orderFilter, setOrderFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /* fetchData: getting employee picking data from packing and formatting data for table */
  const fetchData = async () => {
    try {
      // Get authorization token
      const token = localStorage.getItem("token");

      // Fetch data from the API
      if (token) {
        const response = await axios.get(
          `${API_BASE_URL}/picking_logs/`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );
        setPickingData(response.data);
      }

      else {
        setError("No authorization token found");
        setLoading(false);
        return;
      }

      // Format data for the table
      setRows(
        pickingData.map((row, index) => ({
          key: index + 1,
          warehouse: row.warehouse,
          date: row.date,
          time: row.time,
          employee_id: row.employee_id,
          transaction_type: row.transaction_type,
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
    <div className="dark:bg-gray-900 min-h-screen" >
      <SideBar />
      <NavBar />
      <div className="flex-1 mt-2 dark:bg-gray-900" >
        <div className="flex-1">
          <div className="mt-6 p-10">
            <div className="flex flex-col gap-4">
              <h1 className="text-2xl font-bold mb-6 dark:text-white">Inventory Picking Logs</h1>

              <div className="flex flex-wrap items-center gap-4 mb-6">
                <Input
                  size="md"
                  placeholder="Search Warehouse #"
                  value={warehouseFilter}
                  onChange={(e) => setWarehouseFilter(e.target.value)}
                  className="w-48 rounded border-gray-300 dark:border-gray-600 dark:text-white"
                />
                <Input
                  size="md"
                  placeholder="Search Employee ID"
                  value={employeeFilter}
                  onChange={(e) => setEmployeeFilter(e.target.value)}
                  className="w-48 rounded border-gray-300 dark:border-gray-600 dark:text-white"
                />
                <Input
                  size="md"
                  placeholder="Search Order #"
                  value={orderFilter}
                  onChange={(e) => setOrderFilter(e.target.value)}
                  className="w-48 rounded border-gray-300 dark:border-gray-600 dark:text-white"
                />
              </div>


              {/* Table*/}
              <Table
                aria-label="Inventory picking logs table"
                className="min-w-full dark:bg-transparent"
                classNames={{
                  wrapper: "dark:bg-gray-800 ",
                  th: "dark:bg-gray-700 dark:text-white",
                  tr: "dark:hover:bg-gray-700",
                  td: "dark:text-white dark:before:bg-transparent"
                }}
              >
                <TableHeader>
                  <TableColumn className="dark:text-white">Warehouse #</TableColumn>
                  <TableColumn className="dark:text-white">Date</TableColumn>
                  <TableColumn className="dark:text-white">Time</TableColumn>
                  <TableColumn className="dark:text-white">Employee ID</TableColumn>
                  <TableColumn className="dark:text-white">Transaction Type</TableColumn>
                  <TableColumn className="dark:text-white">Order #</TableColumn>
                  <TableColumn className="dark:text-white">SKU #</TableColumn>
                  <TableColumn className="dark:text-white">Location</TableColumn>
                  <TableColumn className="dark:text-white">Quantity Out</TableColumn>
                </TableHeader>
                <TableBody>
                </TableBody>
              </Table>

              {/* Pagination*/}
              <div className="flex justify-between items-center mt-6">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Page 1 of 1
                </span>
                <Pagination
                  total={1}
                  initialPage={1}
                  current={1}
                  onChange={() => { }}
                  className="text-gray-600 dark:text-gray-400"
                  classNames={{
                    item: "dark:bg-gray-700 dark:text-white",
                    cursor: "bg-black text-white dark:bg-black dark:text-white"
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InventoryPickingLogs