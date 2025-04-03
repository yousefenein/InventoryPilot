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
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
} from "@heroui/react";
import { SearchIcon } from "@heroui/shared-icons";
import { useNavigate, useParams } from "react-router-dom";
import SideBar from "../dashboard_sidebar1/App";
import NavBar from "../navbar/App";
import axios from "axios";
import { Icon } from "@iconify/react";
import { Spinner } from "@heroui/spinner";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Define columns for the inventory table
const inventoryColumns = [
  {
    uid: "picklist_item_id",
    name: "Picklist Item ID",
    sortable: true,
  },
  {
    uid: "area",
    name: "Area",
    sortable: true,
  },
  {
    uid: "lineup_nb",
    name: "Lineup #",
    sortable: false,
  },
  {
    uid: "model_nb",
    name: "Model Type",
    sortable: true,
  },
  {
    uid: "material_type",
    name: "Type",
    sortable: true,
  },
  {
    uid: "sku_color",
    name: "SKU",
    sortable: false,
  },
  {
    uid: "location",
    name: "Location",
    sortable: false,
  },
  {
    uid: "quantity",
    name: "QTY",
    sortable: true,
  },
  
  
  {
    uid: "required_quantity",
    name: "Required Quantity",
    sortable: true,
  },
  {
    uid: "picked_quantity",
    name: "Picked Quantity",
    sortable: false,
  },
  {
    uid: "status",
    name: "Status",
    sortable: false,
  },
  {
    uid: "picked_at",
    name: "Picked At",
    sortable: false,
  },
  {
    uid: "action",
    name: "Action",
    sortable: false,
  },
  {
    uid: "label",
    name: "Label",
    sortable: false,
  },
];

// Function to get default visible columns
const getVisibleColumns = () => {
  return [
    "order_id",
    "area",
    "lineup_nb",
    "model_nb",
    "material_type",
    "sku_color",
    "location",
    "quantity",
    "picklist_item_id",
    "status",
    "action",
    "label",
  ];
};

const InventoryPicklistItem = () => {
  const { order_id } = useParams();
  const [inventoryItems, setInventoryItems] = useState([]);
  const [manufacturingItems, setManufacturingItems] = useState([]);
  const [pickedQuantities, setPickedQuantities] = useState({});
  const [isHovered, setIsHovered] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterValue, setFilterValue] = useState("");
  const [page, setPage] = useState(1);
  const [inventoryPage, setInventoryPage] = useState(1);
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [userData, setUserData] = useState(null);
  const [typeFilter, setTypeFilter] = useState("All");

  // Added for new features
  const [sortDescriptor, setSortDescriptor] = useState({
    column: "area",
    direction: "ascending",
  });
  const [visibleColumns, setVisibleColumns] = useState(new Set(getVisibleColumns()));
  
  const navigate = useNavigate();
  const rowsPerPage = 8;

  const user = localStorage.getItem("user");
  const parsedUser = user ? JSON.parse(user) : null;
  const userRole = parsedUser ? parsedUser.role : null;
  
  const [pickModalOpen, setPickModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);

  const [inventoryError, setInventoryError] = useState(null);
  const [manufacturingError, setManufacturingError] = useState(null);

  // Fetch order items function
  const fetchOrderItems = async (order_id) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No authorization token found");

      const [inventoryResponse, manufacturingResponse] = await Promise.all([
        axios
          .get(
            `${API_BASE_URL}/orders/inventory_picklist_items/${order_id}/`,
            {
              headers: { Authorization: `Bearer ${token}` },
            }
          )
          .catch((error) => {
            setInventoryError("No inventory items found for this order");
            return { data: [] };
          }),
        axios
          .get(
            `${API_BASE_URL}/manufacturingLists/manufacturing_list_item/${order_id}/`,
            {
              headers: { Authorization: `Bearer ${token}` },
            }
          )
          .catch((error) => {
            setManufacturingError(
              "No manufacturing items found for this order"
            );
            return { data: [] };
          }),
      ]);

      console.log("Inventory items data:", inventoryResponse.data);
      
      // Add order_id to each inventory item for sorting and filtering
      const inventoryItemsWithOrderId = inventoryResponse.data.map(item => ({
        ...item,
        order_id: order_id
      }));
      
      setInventoryItems(inventoryItemsWithOrderId);
      setManufacturingItems(manufacturingResponse.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching order items:", err);
      setError("Failed to fetch order items");
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchOrderItems(order_id);
  }, [order_id]);

  // Filter rows for inventory items based on search text
  const filteredInventoryItems = useMemo(() => {
    if (!filterValue.trim()) return inventoryItems;
    const searchTerm = filterValue.toLowerCase();
    return inventoryItems.filter(
      (item) =>
        item.picklist_item_id?.toString().toLowerCase().includes(searchTerm) ||
        item.location?.toLowerCase().includes(searchTerm) ||
        item.sku_color?.toLowerCase().includes(searchTerm) ||
        item.area?.toLowerCase().includes(searchTerm) ||
        item.lineup_nb?.toLowerCase().includes(searchTerm) ||
        item.model_nb?.toLowerCase().includes(searchTerm) ||
        item.material_type?.toLowerCase().includes(searchTerm) ||
        (item.department && item.department.toLowerCase().includes(searchTerm))
    );
  }, [inventoryItems, filterValue]);

  // Sort inventory items
// Sort inventory items
const sortedInventoryItems = useMemo(() => {
  if (!filteredInventoryItems.length) return [];
  
  const itemsCopy = [...filteredInventoryItems];
  
  itemsCopy.sort((a, b) => {
    // First sort by the selected column and direction
    const col = sortDescriptor.column;
    const dir = sortDescriptor.direction === "ascending" ? 1 : -1;
    
    // Special case for material_type - always sort Metal before Plastic regardless of direction
    if (col === "material_type") {
      if (a.material_type === "Metal" && b.material_type === "Plastic") return -1 * dir;
      if (a.material_type === "Plastic" && b.material_type === "Metal") return 1 * dir;
      
      // If both are the same type or neither is Metal/Plastic, use regular string comparison
      const valA = (a[col] || "").toString().toLowerCase();
      const valB = (b[col] || "").toString().toLowerCase();
      return valA.localeCompare(valB) * dir;
    }
    
    // Handle different column types for other columns
    if (col === "picklist_item_id" || col === "quantity") {
      const valA = parseInt(a[col]) || 0;
      const valB = parseInt(b[col]) || 0;
      return (valA - valB) * dir;
    } else {
      const valA = (a[col] || "").toString().toLowerCase();
      const valB = (b[col] || "").toString().toLowerCase();
      return valA.localeCompare(valB) * dir;
    }
  });
  
  return itemsCopy;
}, [filteredInventoryItems, sortDescriptor]);

  // Filter rows for manufacturing items
  const filteredManufacturingItems = useMemo(() => {
    if (!filterValue.trim()) return manufacturingItems;
    const searchTerm = filterValue.toLowerCase();
    return manufacturingItems.filter(
      (item) =>
        item.manufacturing_list_item_id
          ?.toString()
          .toLowerCase()
          .includes(searchTerm) ||
        item.sku_color?.toLowerCase().includes(searchTerm) ||
        item.manufacturing_process?.toLowerCase().includes(searchTerm)
    );
  }, [manufacturingItems, filterValue]);

  // Apply pagination for inventory items
  const paginatedInventoryItems = useMemo(() => {
    const start = (inventoryPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    return sortedInventoryItems.slice(start, end);
  }, [inventoryPage, sortedInventoryItems]);

  // Apply pagination for manufacturing items
  const paginatedManufacturingItems = useMemo(() => {
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    return filteredManufacturingItems.slice(start, end);
  }, [page, filteredManufacturingItems]);

  // Calculate total pages
  const totalInventoryPages = Math.max(
    1,
    Math.ceil(sortedInventoryItems.length / rowsPerPage)
  );
  const totalManufacturingPages = Math.max(
    1,
    Math.ceil(filteredManufacturingItems.length / rowsPerPage)
  );
  
  // Visible columns logic
  const visibleTableColumns = useMemo(() => {
    if (visibleColumns === "all") return inventoryColumns;
    
    return inventoryColumns.filter(
      (column) => Array.from(visibleColumns).includes(column.uid)
    );
  }, [visibleColumns]);
  
  const handlePickedQuantityChange = (picklistItemId, value) => {
    const newQuantity = parseInt(value, 10) || 0;
    setPickedQuantities((prev) => ({
      ...prev,
      [picklistItemId]: newQuantity,
    }));
  };
  
  // Pick Item Logic
  const openPickModal = (item) => {
    setSelectedItem(item);
    setPickModalOpen(true);
  };

  const closePickModal = () => {
    setSelectedItem(null);
    setPickModalOpen(false);
  };

  const handleConfirmPick = async () => {
    if (!selectedItem) return;
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authorization token found");
        return;
      }
    
      const pickedQuantity = pickedQuantities[selectedItem.picklist_item_id] || 0; 
      const requiredQuantity = selectedItem.quantity; 

      closePickModal();
      if (pickedQuantity < requiredQuantity) {
        setPickedQuantities((prev) => ({
          ...prev,
          [selectedItem.picklist_item_id]: "", 
        }));
        alert(`There are missing picks. Please make sure you pick the required quantity.`);
        return; 
      } else if (pickedQuantity > requiredQuantity) {
        setPickedQuantities((prev) => ({
          ...prev,
          [selectedItem.picklist_item_id]: "", 
        }));
        alert(`⚠ Overpicked! Required: ${requiredQuantity}, Picked: ${pickedQuantity}`);
        return; 
      }
      
      await axios.patch(
        `${API_BASE_URL}/inventory/inventory_picklist_items/${selectedItem.picklist_item_id}/pick/`,
        {picked_quantity: pickedQuantity},
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );
      
      setInventoryItems((prev) =>
        prev.map((it) =>
          it.picklist_item_id === selectedItem.picklist_item_id
            ? { ...it, status: true }
            : it
        )
      );
      
    } catch (err) {
      console.error("Error picking item:", err.response?.data || err.message);
      setError("Not allowed, you need to login as a staff");
    }
  };

  const handleLabelClick = (picklistItemId) => {
    navigate(`/label/${picklistItemId}`);
  };

  // Render cell content
  const renderCell = (item, columnKey) => {
    const cellValue = item[columnKey];
    
    switch (columnKey) {
      case "order_id":
        return <div>{order_id}</div>;
      case "picklist_item_id":
        return <div>{item.picklist_item_id}</div>;
      case "location":
        return <div>{item.location || 'N/A'}</div>;
      case "department":
        return <div>{item.department !== null && item.department !== undefined ? item.department : 'N/A'}</div>;
      case "sku_color":
        return <div>{item.sku_color || 'N/A'}</div>;
      case "area":
        return <div>{item.area || 'N/A'}</div>;
      case "lineup_nb":
        return <div>{item.lineup_nb || 'N/A'}</div>;
      case "model_nb":
        return <div>{item.model_nb || 'N/A'}</div>;
      case "material_type":
        return <div>{item.material_type || 'N/A'}</div>;
      case "quantity":
        return <div>{item.quantity}</div>;
      case "picked_quantity":
        return (
          <Input
            type="number"
            min="0"
            size="sm"
            value={pickedQuantities[item.picklist_item_id] || ""}
            onChange={(e) =>
              handlePickedQuantityChange(item.picklist_item_id, e.target.value)
            }
            disabled={item.status} 
          />
        );
      case "status":
        return <div>{item.status ? "Picked" : "To Pick"}</div>;
      case "picked_at":
        return <div>{item.picked_at ? new Date(item.picked_at).toLocaleString() : 'Not picked yet'}</div>;
      case "action":
        return (
          item.status ? (
            <span>Picked</span>
          ) : (
            <input
              type="checkbox"
              checked={pickedQuantities[item.picklist_item_id] === item.quantity}
              onChange={() => openPickModal(item)}
              style={{
                cursor: "pointer", 
              }}
            />
          )
        );
      case "label":
        return (
          <Button 
            style={{
              backgroundColor: '#b91c1c',
              color: 'white',
            }}
            size="sm"
            onPress={() => handleLabelClick(item.picklist_item_id)}>
            View Label
          </Button>
        );
      default:
        return cellValue;
    }
  };

  return (
    <div className="flex h-full">
      <SideBar isOpen={isSidebarOpen} />
           
      <div className="flex-1 sm:ml-10 sm:mt-2">
        <NavBar />

        <div className="flex-1 sm:ml-8">
          <div className="mt-16 p-8">
            <h1 className="text-2xl font-bold mb-6">Order {order_id} Details</h1>

            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
                {error}
              </div>
            )}

            {/* Search, Sort and Column Visibility Controls */}
            <div className="mb-6 flex flex-col sm:flex-row items-center gap-3 sm:gap-4 w-full">
              <Input
                size="md"
                placeholder="Search items"
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
    {inventoryColumns
      .filter(col => col.sortable)
      .map(column => (
        <DropdownItem 
          key={column.uid} 
          onPress={() => setSortDescriptor({ 
            column: column.uid, 
            direction: sortDescriptor.column === column.uid && 
                     sortDescriptor.direction === "ascending" ? "descending" : "ascending" 
          })}
        >
          {column.name}
          {column.uid === "material_type" && (
            <span className="ml-2 text-gray-500 text-xs">
              (Metal always before Plastic)
            </span>
          )}
        </DropdownItem>
      ))
    }
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
                  {inventoryColumns.map((column) => (
                    <DropdownItem key={column.uid}>{column.name}</DropdownItem>
                  ))}
                </DropdownMenu>
              </Dropdown>

              <Button
                style={{
                  color: '#b91c1c',
                  padding: '8px 16px',
                  fontSize: '14px',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s ease',
                }}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                color="default"
                variant="faded"
                onPress={() => {
                  if (userRole === "admin" || userRole === "manager") {
                    navigate("/inventory_and_manufacturing_picklist");
                  } else if (userRole === "staff") {
                    navigate("/inventory_and_manufacturing_picklist");
                  }
                }}
              >
                Go back
              </Button>
            </div>

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div>Loading...</div>
            </div>
          ) : (
            <div>
              {/* Inventory Items Section */}
              <div className="mb-8">
                <h2 className="text-lg font-semibold mb-4">
                  Inventory Pick List Items
                </h2>
                {inventoryError ? (
                  <div className="bg-blue-50 border border-blue-200 text-blue-600 px-4 py-3 rounded">
                    {inventoryError}
                  </div>
                ) : paginatedInventoryItems.length > 0 ? (
                  <>
                    <Table  
                     aria-label="Inventory Pick List"
                     className="min-w-full shadow-lg"
                     isHeaderSticky
                     selectionMode="multiple"
                     bottomContentPlacement="outside"
                     classNames={{
                        td: "before:bg-transparent", 
                      }}
                      topContentPlacement="outside"
                    
                    
                    >
                      <TableHeader className="shadow-xl">
                        <TableColumn className="text-gray-800 font-bold text-base">Picklist Item ID</TableColumn>
                        <TableColumn className="text-gray-800 font-bold text-base">Location</TableColumn>
                        <TableColumn className="text-gray-800 font-bold text-base">SKU Color</TableColumn>
                        <TableColumn className="text-gray-800 font-bold text-base">Area</TableColumn>
                        <TableColumn className="text-gray-800 font-bold text-base">Lineup #</TableColumn>
                        <TableColumn className="text-gray-800 font-bold text-base">Model Type</TableColumn>
                        <TableColumn className="text-gray-800 font-bold text-base">Material Type</TableColumn>
                        <TableColumn className="text-gray-800 font-bold text-base">Required Quantity</TableColumn>
                        <TableColumn className="text-gray-800 font-bold text-base">Picked Quantity</TableColumn>
                        <TableColumn className="text-gray-800 font-bold text-base">Status</TableColumn>
                        <TableColumn className="text-gray-800 font-bold text-base">Picked At</TableColumn>
                        <TableColumn className="text-gray-800 font-bold text-base">Action</TableColumn>
                        <TableColumn className="text-gray-800 font-bold text-base">Label</TableColumn>
                      </TableHeader>
                      <TableBody>
                        {paginatedInventoryItems.map((item) => (
                          <TableRow key={item.picklist_item_id}>
                            <TableCell>{item.picklist_item_id}</TableCell>
                            <TableCell>{item.location}</TableCell>
                            <TableCell>{item.sku_color}</TableCell>
                            <TableCell>{item.area || 'N/A'}</TableCell>
                            <TableCell>{item.lineup_nb || 'N/A'}</TableCell>
                            <TableCell>{item.model_nb || 'N/A'}</TableCell>
                            <TableCell>{item.material_type || 'N/A'}</TableCell>
                            <TableCell>{item.quantity}</TableCell>
                            <TableCell style={{width:"150px", paddingRight:"50px"}}>
                              <Input
                                type="number"
                                min="0"
                                size="sm"
                                value={pickedQuantities[item.picklist_item_id] || ""}
                                onChange={(e) =>
                                  handlePickedQuantityChange(item.picklist_item_id, e.target.value)
                                }
                                disabled={item.status} 
                                />
                            </TableCell>
                            <TableCell>
                              {item.status ? "Picked" : "To Pick"}
                            </TableCell>
                            <TableCell>
                              {item.picked_at ? new Date(item.picked_at).toLocaleString() : 'Not picked yet'}
                            </TableCell>
                            <TableCell>
                              {item.status ? (
                                <span>Picked</span>
                              ) : (
                                <input
                                  type="checkbox"
                                  checked={pickedQuantities[item.picklist_item_id] === item.quantity} // ✅ Checkbox turns blue when correct
                                  onChange={() => openPickModal(item)}
                                  style={{
                                    cursor: "pointer", 
                                  }}
                                />
                              )}
                            </TableCell>
                            <TableCell>
                              <Button 
                              style={{
                               backgroundColor: '#b91c1c',
                               color: 'white',
                              }}
                               size="sm"
                                onPress={() => handleLabelClick(item.picklist_item_id)}>
                                View Label
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>

                      <div className="flex justify-between items-center mt-4">
                        <span>
                          Page {inventoryPage} of {totalInventoryPages}
                        </span>
                        <Pagination
                          total={totalInventoryPages}
                          initialPage={1}
                          current={inventoryPage}
                          onChange={(newPage) => setInventoryPage(newPage)}
                          color="default"
                          classNames={{
                            item: "bg-white text-black",
                            cursor: "bg-black text-white",
                          }}
                        />
                      </div>
                    </>
                  ) : (
                    <div className="bg-blue-50 border border-blue-200 text-blue-600 px-4 py-3 rounded">
                      No inventory items found for this order.
                    </div>
                  )}
                </div>

                <Modal isOpen={pickModalOpen} onClose={closePickModal}>
                  <ModalContent>
                    <div className="p-4">
                      {selectedItem && (
                        <>
                          <h2 className="text-xl font-semibold mb-4">
                            Pick Item Confirmation
                          </h2>
                          <p>
                            Do you want to pick this{" "}
                            <b>{selectedItem.sku_color}</b> item?
                          </p>
                          {/* Display department in confirmation modal */}
                          {selectedItem.department && (
                            <p className="mt-2">
                              <b>Department:</b> {selectedItem.department}
                            </p>
                          )}
                          {selectedItem.area && (
                            <p className="mt-2">
                              <b>Area:</b> {selectedItem.area}
                            </p>
                          )}
                          {selectedItem.lineup_nb && (
                            <p>
                              <b>Lineup:</b> {selectedItem.lineup_nb}
                            </p>
                          )}
                          {selectedItem.model_nb && (
                            <p>
                              <b>Model:</b> {selectedItem.model_nb}
                            </p>
                          )}
                          {selectedItem.material_type && (
                            <p>
                              <b>Material:</b> {selectedItem.material_type}
                            </p>
                          )}

                          <div className="flex justify-end mt-6 gap-4">
                            <Button onPress={closePickModal} color="default">
                              Cancel
                            </Button>
                            <Button onPress={handleConfirmPick} color="primary">
                              Yes, Pick
                            </Button>
                          </div>
                        </>
                      )}
                    </div>
                  </ModalContent>
                </Modal>

                {/* Manufacturing Items Section */}
                <div className="mt-8">
                  <h2 className="text-lg font-semibold mb-4">
                    Manufacturing List Items
                  </h2>
                  {manufacturingError ? (
                    <div className="bg-blue-50 border border-blue-200 text-blue-600 px-4 py-3 rounded">
                      {manufacturingError}
                    </div>
                  ) : paginatedManufacturingItems.length > 0 ? (
                    <>
                      <Table
                        aria-label="Manufacturing List Items"
                        removeWrapper
                        className="bg-gray-200 rounded-lg border-collapse"
                        css={{
                          height: "auto",
                          minWidth: "100%",
                        }}
                        selectionMode="single"
                      >
                        <TableHeader>
                          <TableColumn>Item ID</TableColumn>
                          <TableColumn>SKU Color</TableColumn>
                          <TableColumn>Quantity</TableColumn>
                          <TableColumn>Manufacturing Process</TableColumn>
                          <TableColumn>Process Progress</TableColumn>
                        </TableHeader>
                        <TableBody>
                          {paginatedManufacturingItems.map((item) => (
                            <TableRow key={item.manufacturing_list_item_id}>
                              <TableCell>
                                {item.manufacturing_list_item_id}
                              </TableCell>
                              <TableCell>{item.sku_color}</TableCell>
                              <TableCell>{item.quantity}</TableCell>
                              <TableCell>{item.manufacturing_process}</TableCell>
                              <TableCell>{item.process_progress}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>

                      <div className="flex justify-between items-center mt-4">
                        <span>
                          Page {page} of {totalManufacturingPages}
                        </span>
                        <Pagination
                          total={totalManufacturingPages}
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
                  ) : (
                    <div className="bg-blue-50 border border-blue-200 text-blue-600 px-4 py-3 rounded">
                      No manufacturing items found for this order.
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InventoryPicklistItem;