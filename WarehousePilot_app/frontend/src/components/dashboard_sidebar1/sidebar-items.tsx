import {Icon} from "@iconify/react";
import {type SidebarItem} from "./sidebar";


export function getSidebarItems(): SidebarItem[] {
const user = localStorage.getItem('user');
const parsedUser = user ? JSON.parse(user) : null;
const userRole = parsedUser ? parsedUser.role : null;

//export const items: SidebarItem[] = 
return [
  {
    key: "dashboard",
    href: userRole === 'admin' ? "/admin_dashboard" : "/manager_dashboard",
    icon: "solar:home-2-linear",
    title: "Dashboard",
},
...(userRole === 'admin' ? [
{
  key: "OA Report Input",
  href: "/oa_input",
  icon: "solar:file-text-outline",
  title: "OA Report Input",
},]:[])
,
  ...(userRole === 'admin' || userRole === 'manager' ? 
  [{
    key: "kpi",
    href: "/kpi", 
    icon: "solar:chart-outline",
    title: "KPI",
  },] : [])
  ,
  ...(userRole === 'admin' || userRole === 'manager' ?
    [{
    key: "orders",
    href: "/orders",
    icon: "solar:clipboard-list-linear",
    title: "Orders",
  },] : [])
  ,
  ...(userRole === 'staff'? [{
    key: "staff_assigned_tasks",
    href: "/staff_manufacturing_tasks",
    icon: "solar:bill-list-outline",
    title: "Assigned tasks",
  },] : [])
  ,
  ...(userRole === 'admin' || userRole === 'manager' ? [{
    key: "inventory",
    href: "/inventory-stock",
    icon: "solar:box-outline",
    title: "Inventory",
  },] : [])
  ,
  ...(userRole === 'qa' ? [{
    key: "qa_tasks",
    href: "/qa_tasks",
    icon: "solar:checklist-outline",
    title: "QA Tasks",
  },] : [])
  ,
  ...(userRole === "qa" || userRole === "manager"
  ? [
      {
        key: "qa_error_reports",
        href: "/qa_error_list_view",
        icon: "heroicons-outline:exclamation-circle", // ⚠️ New Exclamation Circle Icon
        title: "QA Error Reports",
      },
    ]
  : []),

  ...(userRole === 'staff' ? [{
    key: "assigned_picklist",
    href: "/assigned_picklist",
    icon: "solar:clipboard-list-outline",
    title: "My Assigned Picklist",
  },] : [])
  ,
  ...(userRole === 'admin' || userRole === 'manager' ? [{
    key: "manufacturing_tasks",
    href: "/manufacturing_tasks",
    icon: "heroicons-outline:cog",
    title: "Manufacturing Tasks",
  }] : [])

,
...(userRole === 'admin' || userRole === 'manager' ? [{
  key: "InventoryPickingLogs",
  href: "/inventory-picking-logs",
  icon: "mdi:file-document-multiple-outline",
  title: "Inventory Picking Logs",
}] : [])
,
{
  key: "account_management",
  href: "/account_management",
  icon: "solar:user-outline",
  title: "Account Management",
}
,

];

}
export default getSidebarItems;
//export default items;