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
} from "@nextui-org/react";
import { SearchIcon } from "@nextui-org/shared-icons";
import axios from "axios";
import SideBar from "../dashboard_sidebar1/App";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";

dayjs.extend(utc);
dayjs.extend(timezone);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const QAErrorListView = () => {
  const [filterValue, setFilterValue] = useState("");
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [page, setPage] = useState(1);
  const rowsPerPage = 10;

  useEffect(() => {
    const fetchQAErrors = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          setErrorMsg("No authorization token found");
          setLoading(false);
          return;
        }
        const response = await axios.get(
          `${API_BASE_URL}/qa_dashboard/qa_tasks/error_reports/`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        setErrors(response.data);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching QA errors:", err);
        setErrorMsg("Failed to fetch QA errors");
        setLoading(false);
      }
    };

    fetchQAErrors();
  }, []);

  const filteredErrors = useMemo(() => {
    if (!filterValue.trim()) return errors;
    const searchTerm = filterValue.toLowerCase();
    return errors.filter((err) =>
      [err.subject, err.comment, err.manufacturing_task_id?.toString()]
        .some((value) => value?.toLowerCase().includes(searchTerm))
    );
  }, [errors, filterValue]);

  const startIndex = (page - 1) * rowsPerPage;
  const endIndex = startIndex + rowsPerPage;
  const paginatedErrors = filteredErrors.slice(startIndex, endIndex);
  const totalPages = Math.ceil(filteredErrors.length / rowsPerPage);

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <SideBar />

      {/* Main Content */}
      <div className="flex-1">
        <div className="mt-16 p-8">
          <div className="flex flex-col gap-6">
            {/* Title on Separate Line */}
            <div>
              <h1 className="text-2xl font-bold mb-6">QA Error Reports</h1>
            </div>

            {/* Error Message */}
            {errorMsg && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                {errorMsg}
              </div>
            )}

            {/* Search Bar */}
            <Input
              size="md"
              placeholder="Search QA errors..."
              value={filterValue}
              onChange={(e) => setFilterValue(e.target.value)}
              endContent={<SearchIcon className="text-default-400" width={16} />}
              className="w-72 mb-4"
            />

            {/* Table Data */}
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div>Loading...</div>
              </div>
            ) : (
              <>
                <Table aria-label="QA Error list" className="min-w-full">
                  <TableHeader>
                    <TableColumn>ID</TableColumn>
                    <TableColumn>Subject</TableColumn>
                    <TableColumn>Comment</TableColumn>
                    <TableColumn>Task ID</TableColumn>
                    <TableColumn>Task Status</TableColumn>
                    <TableColumn>Reported By</TableColumn>
                    <TableColumn>Created At</TableColumn>
                  </TableHeader>
                  <TableBody items={paginatedErrors}>
                    {(item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.id}</TableCell>
                        <TableCell>{item.subject}</TableCell>
                        <TableCell>{item.comment}</TableCell>
                        <TableCell>{item.manufacturing_task_id}</TableCell>
                        <TableCell>{item.task_status}</TableCell>
                        <TableCell>{item.reported_by}</TableCell>
                        <TableCell>
                          {dayjs.utc(item.created_at)
                            .tz("America/Toronto")
                            .format("YYYY-MM-DD HH:mm")}
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>

                {/* Pagination */}
                <div className="flex justify-between items-center mt-4">
                  <span>
                    Page {page} of {totalPages}
                  </span>
                  <Pagination
                    total={totalPages}
                    page={page}
                    initialPage={1}
                    onChange={(newPage) => setPage(newPage)}
                    color="default"
                    classNames={{
                      item: "bg-white text-black",
                      cursor: "bg-black text-white",
                    }}
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

export default QAErrorListView;




