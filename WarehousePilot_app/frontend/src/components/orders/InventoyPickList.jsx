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
  Modal,
  ModalContent,
  Select,
  SelectItem,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
} from "@heroui/react";
import { SearchIcon } from "@heroui/shared-icons";
import axios from "axios";
import { Spinner } from "@heroui/spinner";
import { useNavigate } from "react-router-dom";
import { color } from "framer-motion";
import CopyText from "../orders/copy-text";
import { Icon } from "@iconify/react";
import { Chip } from "@heroui/react";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Define columns for table
const columns = [
  {
    uid: "order_id",
    name: "Order ID",
    sortable: true,
  },
  {
    uid: "due_date",
    name: "Due Date",
    sortable: true,
  },
  {
    uid: "already_filled",
    name: "Already Filled",
    sortable: true,
  },
  {
    uid: "assigned_to",
    name: "Assigned To",
    sortable: true,
  },
  {
    uid: "actions",
    name: "Action",
    sortable: false,
  },
];

// Function to get default visible columns
const getVisibleColumns = () => {
  return columns.map(column => column.uid);
};

const InventoryPickList = () => {
  const [filterValue, setFilterValue] = useState("");
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [userData, setUserData] = useState(null);
  const rowsPerPage = 10;
  const navigate = useNavigate();

  // For staff assignment modal
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [staffList, setStaffList] = useState([]);
  const [staffSearchTerm, setStaffSearchTerm] = useState("");
  const [selectedStaffId, setSelectedStaffId] = useState(null);
  const [assigningOrderId, setAssigningOrderId] = useState(null);
  
  // Added sort descriptor state
  const [sortDescriptor, setSortDescriptor] = useState({ 
    column: "order_id", 
    direction: "ascending" 
  });
  
  // Column visibility state
  const [visibleColumns, setVisibleColumns] = useState(new Set(getVisibleColumns()));

  // Filter rows by search text
  const filteredRows = useMemo(() => {
    if (!filterValue.trim()) return rows;
    
    const searchTerm = filterValue.toLowerCase();
    
    return rows.filter((row) => {
      const orderIdMatch = row.order_id?.toString().toLowerCase().includes(searchTerm);
      const dueDateMatch = row.due_date?.toLowerCase().includes(searchTerm);
      const assignedToMatch = row.assigned_to?.toLowerCase().includes(searchTerm);
      const alreadyFilledMatch = searchTerm === "yes" ? row.already_filled : 
                                 searchTerm === "no" ? !row.already_filled : false;
      
      return orderIdMatch || dueDateMatch || assignedToMatch || alreadyFilledMatch;
    });
  }, [rows, filterValue]);

  const sortedFilteredRows = useMemo(() => {
    const rowsCopy = [...filteredRows];
  
    const col = sortDescriptor.column;
  
    if (col === "due_date") {
      // Split rows with known and unknown due dates
      const withDueDate = rowsCopy.filter(row => row.due_date);
      const withoutDueDate = rowsCopy.filter(row => !row.due_date);
  
      withDueDate.sort((a, b) => {
        const dateA = new Date(a.due_date);
        const dateB = new Date(b.due_date);
        return sortDescriptor.direction === "ascending"
          ? dateA - dateB
          : dateB - dateA;
      });
  
      // Append unknowns at the end
      return [...withDueDate, ...withoutDueDate];
    }
  
    // Other sorting cases
    rowsCopy.sort((a, b) => {
      if (col === "order_id") {
        const numA = Number(a[col]) || 0;
        const numB = Number(b[col]) || 0;
        return sortDescriptor.direction === "ascending"
          ? numA - numB
          : numB - numA;
      }
  
      if (col === "already_filled") {
        const boolA = Boolean(a[col]);
        const boolB = Boolean(b[col]);
        return sortDescriptor.direction === "ascending"
          ? boolA === boolB ? 0 : boolA ? 1 : -1
          : boolA === boolB ? 0 : boolA ? -1 : 1;
      }
  
      if (col === "assigned_to") {
        const strA = a[col]?.toLowerCase() || "";
        const strB = b[col]?.toLowerCase() || "";
        return sortDescriptor.direction === "ascending"
          ? strA.localeCompare(strB)
          : strB.localeCompare(strA);
      }
  
      return 0;
    });
  
    return rowsCopy;
  }, [filteredRows, sortDescriptor]);
  
  // Apply pagination
  const paginatedRows = useMemo(() => {
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;

    // If the filtered list has fewer pages, reset page number
    if (start >= sortedFilteredRows.length) {
      setPage(1); // Reset to first page if page number is out of range
    }

    return sortedFilteredRows.slice(start, end);
  }, [page, sortedFilteredRows]);

  // Calculate total pages
  const totalPages = Math.max(
    1,
    Math.ceil(sortedFilteredRows.length / rowsPerPage)
  );
  
  // Filter columns based on visibility settings
  const visibleTableColumns = useMemo(() => {
    if (visibleColumns === "all") return columns;
    
    return columns.filter(
      (column) => Array.from(visibleColumns).includes(column.uid)
    );
  }, [visibleColumns]);

  const fetchPickList = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authorization token found");
        setLoading(false);
        return;
      }

      const response = await axios.get(
        `${API_BASE_URL}/orders/inventory_picklist/`,
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
          due_date: row.due_date,
          already_filled: row.already_filled,
          assigned_to: row.assigned_to,
        }))
      );
      setLoading(false);
    } catch (err) {
      console.error("Error fetching inventory pick list:", err);
      setError("Failed to fetch inventory pick list");
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPickList();
  }, []);

  const handleViewOrderDetails = (order_id) => {
    navigate(`/inventory_picklist_items/${order_id}`);
  };

  // Staff assignment modal
  // Open the modal for a specific order
  const handleOpenAssignModal = async (orderId) => {
    setAssigningOrderId(orderId);
    setAssignModalOpen(true);
    setSelectedStaffId(null);

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authorization token found");
        return;
      }
      const staffResp = await axios.get(`${API_BASE_URL}/auth/retrieve_users`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      // staffResp.data => array of staff like [{ id, first_name, last_name }, ...]
      setStaffList(staffResp.data);
      console.log("staffResp.data =>", staffResp.data);
    } catch (err) {
      console.error("Error fetching staff:", err);
      setError("Failed to fetch staff list");
    }
  };

  // Filter staff by staffSearchTerm
  const filteredStaffList = useMemo(() => {
    if (!staffSearchTerm.trim()) return staffList;
    const lower = staffSearchTerm.toLowerCase();
    return staffList.filter((staff) => {
      const fullName = (staff.first_name + staff.last_name).toLowerCase();
      return fullName.includes(lower);
    });
  }, [staffList, staffSearchTerm]);

  // Confirm assignment
  const handleConfirmAssign = async () => {
    console.log("Inputed selected staff:" + selectedStaffId);
    if (!selectedStaffId) {
      alert("Please select a staff user");
      return;
    }
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authorization token found");
        return;
      }
      await axios.post(
        `${API_BASE_URL}/inventory/assign_order/${assigningOrderId}`,
        { user_id: selectedStaffId },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );
      // Update local state
      const staffObj = staffList.find((st) => st.user_id === selectedStaffId);
      const staffName = staffObj
        ? `${staffObj.first_name} ${staffObj.last_name}`
        : "Unassigned";

      setRows((prev) =>
        prev.map((row) =>
          row.order_id === assigningOrderId
            ? { ...row, assigned_to: staffName }
            : row
        )
      );
      setAssignModalOpen(false);
    } catch (err) {
      console.error("Error assigning staff:", err);
      setError("Failed to assign staff");
    }
  };

  // Close modal
  const handleCloseModal = () => {
    setAssignModalOpen(false);
    setStaffSearchTerm("");
    setSelectedStaffId(null);
    setAssigningOrderId(null);
  };
  
  // Render a table cell based on column key
  const renderCell = (item, columnKey) => {
    const cellValue = item[columnKey];
    
    switch (columnKey) {
      case "order_id":
        return (
          <div className="flex items-center">
            {item.order_id}
            <CopyText text={item.order_id.toString()} />
          </div>
        );
        case "due_date":
          return item.due_date ? (
            <div className="flex items-center gap-2">
              <Icon
                icon="solar:calendar-linear"
                width={18}
                className="text-gray-500"
              />
              {item.due_date}
            </div>
          ) : (
           
            <Chip
                  className="text-black-400 italic"
                  color="default"
                  size="sm"
                  variant="flat"
                >
                  Not set
                </Chip>
          );
          case "already_filled":
            return item.already_filled ? "Yes" : "No";
          case "assigned_to":
            return (
              item.assigned_to ? (
                <Chip
                  className="capitalize"
                  color="success"
                  size="sm"
                  variant="flat"
                >
                  {item.assigned_to}
                </Chip>
              ) : (
                <Chip
                  className="capitalize"
                  color="default"
                  size="sm"
                  variant="flat"
                >
                  Unassigned
                </Chip>
              )
            );
          case "actions":
      
      
        return (
          <>
            <Button
              style={{
                backgroundColor: '#b91c1c',
                color: 'white',
              }}
              size="sm"
              onPress={() => handleViewOrderDetails(item.order_id)}
            >
              Pick Order
            </Button>
            <Button
              style={{
                backgroundColor: '#b91c1c',
                color: 'white',
              }}
              size="sm"
              onPress={() => handleOpenAssignModal(item.order_id)}
              className="ml-2"
            >
              Assign Staff
            </Button>
          </>
        );
      default:
        return cellValue;
    }
  };

  return (
    <div className="mt-16 p-8">
      <h1 className="text-2xl font-bold mb-6">Inventory Pick List</h1>
      <h6 className="text-md font-bold">
        Few examples to test the different cases of orders being picked
      </h6>
      <p>
        order have both inventory picklist and manufacturinglist 90171, 89851
        ,89672
      </p>
      <p>order have both inventory picklist and no manufacturinglist 80555 </p>
      <p>order have none 89345 </p>

      {/* Error message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
          {error}
        </div>
      )}

      {/* Search, Sort and Column Visibility Controls */}
      <div className="mb-6 flex flex-col sm:flex-row items-center gap-3 sm:gap-4 w-full">
        <Input
          size="md"
          placeholder="Search by order ID, due date, or assignment"
          value={filterValue}
          onChange={(e) => setFilterValue(e.target.value)}
          endContent={<SearchIcon className="text-default-400" width={16} />}
          className="w-full sm:w-72"
        />
        
        {/* Sort Dropdown */}
        <Dropdown>
          <DropdownTrigger>
            <Button 
              variant="flat" 
              startContent={<Icon icon="mdi:sort" width={16} />}
              style={{ backgroundColor: '#f3f4f6', color: '#000' }}
            >
              Sort by {sortDescriptor.column} ({sortDescriptor.direction})
            </Button>
          </DropdownTrigger>
          <DropdownMenu aria-label="Sort options">
            <DropdownItem 
              key="order_id" 
              onPress={() => setSortDescriptor({ 
                column: "order_id", 
                direction: sortDescriptor.column === "order_id" && sortDescriptor.direction === "ascending" ? "descending" : "ascending" 
              })}
            >
              Order ID
            </DropdownItem>
            <DropdownItem 
              key="due_date" 
              onPress={() => setSortDescriptor({ 
                column: "due_date", 
                direction: sortDescriptor.column === "due_date" && sortDescriptor.direction === "ascending" ? "descending" : "ascending" 
              })}
            >
              Due Date
            </DropdownItem>
            
          </DropdownMenu>
        </Dropdown>
        
        {/* Column Visibility Dropdown */}
        <Dropdown closeOnSelect={false}>
          <DropdownTrigger>
            <Button 
              variant="flat" 
              startContent={<Icon icon="material-symbols:view-column" width={16} />}
              style={{ backgroundColor: '#f3f4f6', color: '#000' }}
            >
              Columns
            </Button>
          </DropdownTrigger>
          <DropdownMenu 
            disallowEmptySelection
            aria-label="Column Visibility"
            selectedKeys={visibleColumns}
            selectionMode="multiple"
            onSelectionChange={setVisibleColumns}
          >
            {columns.map((column) => (
              <DropdownItem key={column.uid}>{column.name}</DropdownItem>
            ))}
          </DropdownMenu>
        </Dropdown>
        
        <Button
          color="default"
          variant="faded"
          onPress={() => navigate("/orders")}
        >
          Go back
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64 text-sm">
          Loading...
          <Spinner size="lg" color="default" className="ms-5"/>
        </div>
      ) : (
        <>
          <Table
            aria-label="Inventory Pick List"
            className="min-w-full shadow-lg"
            isHeaderSticky
            bottomContentPlacement="outside"
            selectionMode="multiple"
            classNames={{
              td: "before:bg-transparent",
            }}
            topContentPlacement="outside"
            sortDescriptor={sortDescriptor}
            onSortChange={setSortDescriptor}
          >
            <TableHeader className="shadow-xl">
              {visibleTableColumns.map((column) => (
                <TableColumn 
                  key={column.uid} 
                  className="text-gray-800 font-bold text-lg"
                  allowsSorting={column.sortable}
                >
                  {column.name}
                </TableColumn>
              ))}
            </TableHeader>

            <TableBody items={paginatedRows}>
              {(item) => (
                <TableRow key={item.id}>
                  {visibleTableColumns.map((column) => (
                    <TableCell key={`${item.id}-${column.uid}`}>
                      {renderCell(item, column.uid)}
                    </TableCell>
                  ))}
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
              color="default"
              classNames={{
                item: "bg-white text-black",
                cursor: "bg-black text-white",
              }}
            />
          </div>
        </>
      )}
      
      {/* Staff Assignment Modal */}
      <Modal isOpen={assignModalOpen} onClose={handleCloseModal} isDismissable={false}>
        <ModalContent>
          <div className="p-4">
            <h2 className="text-xl font-semibold mb-4">Assign Staff</h2>

            {/* Search bar for staff */}
            <Input
              size="md"
              placeholder="Search staff"
              value={staffSearchTerm}
              onChange={(e) => setStaffSearchTerm(e.target.value)}
              className="mb-3"
            />

            {/* Staff dropdown */}
            <Select
              label="Assign Staff"
              placeholder="Select a staff member"
              value={selectedStaffId ? selectedStaffId.toString() : undefined}
              onChange={(newVal) => {
                console.log("Dropdown value:", newVal.target.value);
                setSelectedStaffId(Number(newVal.target.value));
                console.log("Selected staff:" + selectedStaffId);
              }}
              className="w-full"
            >
              {filteredStaffList
                .filter((staff) => staff.role === "staff")
                .map((staff) => {
                  const fullName = `${staff.first_name} ${staff.last_name}`;
                  return (
                    <SelectItem key={staff.user_id} value={staff.user_id}>
                      {fullName}
                    </SelectItem>
                  );
                })}
            </Select>
            <div className="flex justify-end mt-6 gap-4">
              <Button onPress={handleCloseModal} color="default">
                Cancel
              </Button>
              <Button onPress={handleConfirmAssign} style={{ backgroundColor: '#b91c1c', color:'white'}} >
                Confirm
              </Button>
            </div>
          </div>
        </ModalContent>
      </Modal>
    </div>
  );
};

export default InventoryPickList;