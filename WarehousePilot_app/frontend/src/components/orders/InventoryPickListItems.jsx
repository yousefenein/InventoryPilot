import React, { useState, useEffect } from "react";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Pagination,
} from "@nextui-org/react";
import { useParams } from "react-router-dom";
import axios from "axios";

const InventoryPicklistItems = () => {
  const { order_id } = useParams();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
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

  // Apply pagination
  const paginatedItems = items.slice(
    (page - 1) * rowsPerPage,
    page * rowsPerPage
  );

  const totalPages = Math.ceil(items.length / rowsPerPage);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Picklist Items for Order {order_id}</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
          {error}
        </div>
      )}

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
  );
};

export default InventoryPicklistItems;
