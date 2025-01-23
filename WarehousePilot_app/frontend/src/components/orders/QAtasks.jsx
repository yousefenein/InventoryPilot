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
  Select,
  SelectItem,
} from "@nextui-org/react";
import { SearchIcon } from "@nextui-org/shared-icons";
import axios from "axios";
import SideBar from "../dashboard_sidebar1/App";
import Header from "../dashboard_sidebar/Header";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";

dayjs.extend(utc);
dayjs.extend(timezone);

const QATasks = () => {
  const [filterValue, setFilterValue] = useState("");
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const rowsPerPage = 10;

  // Fetch QA tasks
  const fetchTasks = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authorization token found");
        setLoading(false);
        return;
      }
      const response = await axios.get(
        "http://127.0.0.1:8000/qa_dashboard/qa_tasks/",
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
          manufacturing_id: row.manufacturing_task_id,
          qty: row.qty,
          status: row.status,
          sku_color: row.sku_color_id,
          due_date: row.due_date || "N/A",
          prod_qa: row.prod_qa ? "Completed" : "Pending",
          paint_qa: row.paint_qa ? "Completed" : "Pending",
        }))
      );
      setLoading(false);
    } catch (err) {
      console.error("Error fetching QA tasks:", err);
      setError("Failed to fetch QA tasks");
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleUpdate = async (taskId, prodQa, paintQa) => {
    try {
      await axios.post(
        "http://127.0.0.1:8000/qa_dashboard/qa_tasks/update/",
        {
          manufacturing_task_id: taskId,
          prod_qa: prodQa,
          paint_qa: paintQa,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
            "Content-Type": "application/json",
          },
        }
      );
      fetchTasks(); // Refresh data after update
    } catch (error) {
      console.error("Error updating QA task:", error);
    }
  };

  const filteredRows = useMemo(() => {
    if (!filterValue.trim()) return rows;
    const searchTerm = filterValue.toLowerCase();
    return rows.filter((row) => {
      return Object.values(row).some((value) =>
        value?.toString().toLowerCase().includes(searchTerm)
      );
    });
  }, [rows, filterValue]);

  const paginatedRows = useMemo(() => {
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    return filteredRows.slice(start, end);
  }, [page, filteredRows]);

  const totalPages = Math.ceil(filteredRows.length / rowsPerPage);

  return (
    <div className="flex h-full">
      <SideBar />
      <div className="flex-1">
        <div className="mt-16 p-8">
          <div className="flex flex-col gap-6">
            <h1 className="text-2xl font-bold mb-6">QA Tasks</h1>
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}
            <Input
              size="md"
              placeholder="Search tasks"
              value={filterValue}
              onChange={(e) => setFilterValue(e.target.value)}
              endContent={<SearchIcon className="text-default-400" width={16} />}
              className="w-72 mb-4"
            />
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div>Loading...</div>
              </div>
            ) : (
              <>
                <Table aria-label="QA tasks" className="min-w-full">
                  <TableHeader>
                    <TableColumn>Manu ID</TableColumn>
                    <TableColumn>Qty</TableColumn>
                    <TableColumn>SKU ID</TableColumn>
                    <TableColumn>Due Date</TableColumn>
                    <TableColumn>Production QA</TableColumn>
                    <TableColumn>Paint QA</TableColumn>
                    <TableColumn>Action</TableColumn>
                  </TableHeader>
                  <TableBody items={paginatedRows}>
                    {(item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.manufacturing_id}</TableCell>
                        <TableCell>{item.qty}</TableCell>
                        <TableCell>{item.sku_color}</TableCell>
                        <TableCell>
                          {item.due_date
                            ? dayjs(item.due_date).format("YYYY-MM-DD")
                            : "N/A"}
                        </TableCell>
                        <TableCell>
                          <Select
                            size="sm"
                            value={item.prod_qa}
                            onChange={(e) =>
                              handleUpdate(
                                item.manufacturing_id,
                                e.target.value,
                                item.paint_qa
                              )
                            }
                          >
                            <SelectItem value="Pending">Pending</SelectItem>
                            <SelectItem value="Completed">Completed</SelectItem>
                          </Select>
                        </TableCell>
                        <TableCell>
                          <Select
                            size="sm"
                            value={item.paint_qa}
                            onChange={(e) =>
                              handleUpdate(
                                item.manufacturing_id,
                                item.prod_qa,
                                e.target.value
                              )
                            }
                          >
                            <SelectItem value="Pending">Pending</SelectItem>
                            <SelectItem value="Completed">Completed</SelectItem>
                          </Select>
                        </TableCell>
                        <TableCell>
                          <Button
                            size="sm"
                            variant="shadow"
                            color="primary"
                            onClick={() =>
                              handleUpdate(item.manufacturing_id, "Completed", "Completed")
                            }
                          >
                            Complete
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
    </div>
  );
};

export default QATasks;

