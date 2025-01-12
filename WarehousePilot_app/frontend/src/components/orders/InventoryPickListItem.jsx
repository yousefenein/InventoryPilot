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

import { useParams } from "react-router-dom";

const InventoryPicklistItem = () => {
  const { order_id } = useParams();
  const [filterValue, setFilterValue] = useState("");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [userData, setUserData] = useState(null);
  const rowsPerPage = 10;

  // Fetch picklist items for the given order
  const fetchPicklistItems = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authorization token found");
        setLoading(false);
        return;
      }
      
      const response = await axios.get(
        `http://127.0.0.1:8000/orders/inventory_picklist_items/${order_id}/`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      setItems(response.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching picklist items:", err);
      setError("Failed to fetch picklist items");
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPicklistItems();
  }, [order_id]);

  // Filter rows by search text
  const filteredItems = useMemo(() => {
    if (!filterValue.trim()) return items;
    const searchTerm = filterValue.toLowerCase();
    return items.filter((item) => {
      const picklistIdMatch = item.picklist_item_id
        ?.toString()
        .toLowerCase()
        .includes(searchTerm);
      const locationMatch = item.location?.toLowerCase().includes(searchTerm);
      const skuColorMatch = item.sku_color?.toLowerCase().includes(searchTerm);
      return picklistIdMatch || locationMatch || skuColorMatch;
    });
  }, [items, filterValue]);

  // Apply pagination
  const paginatedItems = useMemo(() => {
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    return filteredItems.slice(start, end);
  }, [page, filteredItems]);

  const totalPages = Math.ceil(filteredItems.length / rowsPerPage);

  return (
    <div className="flex h-full">
         <SideBar isOpen={isSidebarOpen} />

      <div className="flex-1 sm:ml-8">
      
        <div className="mt-16 p-8">
          <h1 className="text-2xl font-bold mb-6">
            Picklist Items for Order {order_id}
          </h1>

          {/* Error message */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
              {error}
            </div>
          )}

          {/* Search Input */}
          <div className="mb-6 flex items-center gap-2">
            <Input
              size="md"
              placeholder="Search items"
              value={filterValue}
              onChange={(e) => setFilterValue(e.target.value)}
              endContent={<SearchIcon className="text-default-400" width={16} />}
              className="w-72"
            />
          </div>

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div>Loading...</div>
            </div>
          ) : (
            <>
              <Table aria-label="Picklist Items" className="min-w-full">
                <TableHeader>
                  <TableColumn>Picklist Item ID</TableColumn>
                  <TableColumn>Location</TableColumn>
                  <TableColumn>SKU Color</TableColumn>
                  <TableColumn>Quantity</TableColumn>
                  <TableColumn>Status</TableColumn>
                </TableHeader>
                <TableBody items={paginatedItems}>
                  {(item) => (
                    <TableRow key={item.picklist_item_id}>
                      <TableCell>{item.picklist_item_id}</TableCell>
                      <TableCell>{item.location}</TableCell>
                      <TableCell>{item.sku_color}</TableCell>
                      <TableCell>{item.quantity}</TableCell>
                      <TableCell>{item.status}</TableCell>
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

export default InventoryPicklistItem;
