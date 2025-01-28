import {DangerCircleSvg} from "./danger-circle";
import {DefaultCircleSvg} from "./default-circle";
import {SuccessCircleSvg} from "./success-circle";
import {WarningCircleSvg} from "./warning-circle";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export type ManufacturingTask = {
  manufacturing_task_id: number;
  sku_color: string;
  qty: number;
  due_date: string;
  status: string;
  nesting_start_time?: string;
  nesting_end_time?: string;
  nesting_employee?: string;
  bending_start_time?: string;
  bending_end_time?: string;
  bending_employee?: string;
  cutting_start_time?: string;
  cutting_end_time?: string;
  cutting_employee?: string;
  welding_start_time?: string;
  welding_end_time?: string;
  welding_employee?: string;
  paint_start_time?: string;
  paint_end_time?: string;
  paint_employee?: string;
};

export type ColumnsKey =
  | "manufacturing_task_id"
  | "sku_color"
  | "qty"
  | "due_date"
  | "status"
  | "nesting_start_time"
  | "nesting_end_time"
  | "nesting_employee"
  | "bending_start_time"
  | "bending_end_time"
  | "bending_employee"
  | "cutting_start_time"
  | "cutting_end_time"
  | "cutting_employee"
  | "welding_start_time"
  | "welding_end_time"
  | "welding_employee"
  | "paint_start_time"
  | "paint_end_time"
  | "paint_employee";

export const columns = [
  {name: "Task ID", uid: "manufacturing_task_id"},
  {name: "SKU Color", uid: "sku_color"},
  {name: "Quantity", uid: "qty"},
  {name: "Due Date", uid: "due_date"},
  {name: "Status", uid: "status"},
  {name: "Nesting Start Time", uid: "nesting_start_time"},
  {name: "Nesting End Time", uid: "nesting_end_time"},
  {name: "Nesting Employee", uid: "nesting_employee"},
  {name: "Bending Start Time", uid: "bending_start_time"},
  {name: "Bending End Time", uid: "bending_end_time"},
  {name: "Bending Employee", uid: "bending_employee"},
  {name: "Cutting Start Time", uid: "cutting_start_time"},
  {name: "Cutting End Time", uid: "cutting_end_time"},
  {name: "Cutting Employee", uid: "cutting_employee"},
  {name: "Welding Start Time", uid: "welding_start_time"},
  {name: "Welding End Time", uid: "welding_end_time"},
  {name: "Welding Employee", uid: "welding_employee"},
  {name: "Paint Start Time", uid: "paint_start_time"},
  {name: "Paint End Time", uid: "paint_end_time"},
  {name: "Paint Employee", uid: "paint_employee"},
];

export const getVisibleColumns = (): ColumnsKey[] => {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const department = user.department;

  const baseColumns: ColumnsKey[] = [
    "manufacturing_task_id",
    "sku_color",
    "qty",
    "due_date",
    "status",
  ];

  switch (department) {
    case "nesting":
      return [...baseColumns, "nesting_start_time", "nesting_end_time", "nesting_employee"];
    case "bending":
      return [...baseColumns, "bending_start_time", "bending_end_time", "bending_employee"];
    case "cutting":
      return [...baseColumns, "cutting_start_time", "cutting_end_time", "cutting_employee"];
    case "welding":
      return [...baseColumns, "welding_start_time", "welding_end_time", "welding_employee"];
    case "painting":
      return [...baseColumns, "paint_start_time", "paint_end_time", "paint_employee"];
    default:
      return baseColumns;
  }
};

export const fetchManufacturingTasks = async (): Promise<ManufacturingTask[]> => {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const department = user.department;

  const response = await fetch(`${API_BASE_URL}/manufacturingLists/manufacturing_tasks/?department=${department}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    }
  );
  if (!response.ok) {
    throw new Error("Failed to fetch manufacturing tasks");
  }
  const data = await response.json();
  return data;
};






