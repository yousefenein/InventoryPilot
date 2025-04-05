import {DangerCircleSvg} from "./danger-circle";
import {DefaultCircleSvg} from "./default-circle";
import {SuccessCircleSvg} from "./success-circle";
import {WarningCircleSvg} from "./warning-circle";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const statusOptions = [
  {name: "Low", uid: "low"},
  {name: "Moderate", uid: "moderate"},
  {name: "High", uid: "high"},
  {name: "Out of Stock", uid: "out_of_stock"},
] as const;

export type StatusOptions = (typeof statusOptions)[number]["name"];

export const statusColorMap: Record<StatusOptions, JSX.Element> = {
  Low: DangerCircleSvg,
  Moderate: WarningCircleSvg,
  High: SuccessCircleSvg,
  "Out of Stock": DefaultCircleSvg,
};

export type Inventory = {
  inventory_id: number;
  location: string;
  sku_color_id: string;
  qty: number;
  warehouse_number: string;
  amount_needed: number;
  status: StatusOptions;
};

export type ColumnsKey =
  | "inventory_id"
  | "location"
  | "sku_color_id"
  | "qty"
  | "warehouse_number"
  | "amount_needed"
  | "status"
  | "edit";

export const INITIAL_VISIBLE_COLUMNS: ColumnsKey[] = [
  "inventory_id",
  "location",
  "sku_color_id",
  "qty",
  "warehouse_number",
  "amount_needed",
  "status",
  "edit",
];

export const columns = [
  {name: "Warehouse Number", uid: "warehouse_number"},
  {name: "SKU Color ID", uid: "sku_color_id"},
  {name: "Location", uid: "location"},
  {name: "Quantity", uid: "qty"},
  {name: "Inventory ID", uid: "inventory_id"},
  {name: "Amount Needed", uid: "amount_needed"},
  {name: "Stock Level", uid: "status"},
  {name: "Edit", uid: "edit"},
];

export const fetchInventoryData = async (): Promise<Inventory[]> => {
  const response = await fetch(`${API_BASE_URL}/inventory`);
  if (!response.ok) {
    throw new Error("Failed to fetch inventory data");
  }
  const data = await response.json();
  if (!Array.isArray(data.inventory)) {
    throw new Error("Invalid inventory data format");
  }
  return data.inventory.map((item: any) => ({
    ...item,
    status: item.status as StatusOptions,
  }));
};

export const getCsrfToken = async (): Promise<string> => {
  const response = await fetch(`${API_BASE_URL}/inventory/csrf-token`);
  if (!response.ok) {
    throw new Error("Failed to fetch CSRF token");
  }
  const data = await response.json();
  return data.csrfToken;
};

export const deleteInventoryItems = async (itemIds: number[]): Promise<void> => {
  const csrfToken = await getCsrfToken();
  const response = await fetch(`${API_BASE_URL}/inventory/delete`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({ item_ids: itemIds }),
  });
  if (!response.ok) {
    throw new Error("Failed to delete inventory items");
  }
};

export const editInventoryItem = async (item: {
  inventory_id: number;
  warehouse_number: string;
  sku_color_id: string;
  location: string;
  qty: number;
  amount_needed: number;
}): Promise<void> => {
  const csrfToken = await getCsrfToken();
  const response = await fetch(`${API_BASE_URL}/inventory/update_inventory_item`, { // Updated path
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify(item),
  });
  if (!response.ok) {
    throw new Error("Failed to update inventory item");
  }
};
