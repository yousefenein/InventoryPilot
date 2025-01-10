import { Dashboard, ManagerDashboard, AdminDashboard, AccountManagement, ChangePassword, Profile  } from '../dashboard';
import KpiDashboard from "../dashboard/KpiDashboard"
import InventoryTable from '../inventory-stock/App'; 
import ManageUsersPage from '../admin_manage_users/ManageUsersPage';
import AddUsersDashboard from '../dashboard/AddUsersDashboard';
import NotifCard from '../notifications/notifications-card/App';
import NavBar from '../navbar/App';
import OrderListView from '../orders/OrderListView'; 
import ManageUsersTable from '../admin_manage_users/manage_users_table/App';
import InventoryPickListItems from '../orders/InventoryPickListItems';
import InventoryAndManufacturingList from '../orders/InventoryAndManufacturingList';


export const dashboard_routes = [
  { path: '/dashboard', element: <Dashboard /> },
  { path: '/manager_dashboard', element: <ManagerDashboard /> },
  { path: '/admin_dashboard', element: <AdminDashboard /> },
  { path: '/admin_dashboard/manage_users', element: <ManageUsersTable /> },
  { path: '/account_management', element: <AccountManagement /> },
  { path: '/profile', element: <Profile /> },
  { path: '/kpi', element: <KpiDashboard /> },
  { path: '/change_password', element: <ChangePassword /> },
  { path: '/inventory-stock', element: <InventoryTable /> },
  {path: '/admin_dashboard/add_users', element: <AddUsersDashboard />},
  { path: '/navbar', element: <NavBar /> },
  {path: '/admin_dashboard/edit_user/:user_id', element: <AddUsersDashboard />},
  { path: '/admin_dashboard/add_users', element: <AddUsersDashboard />},
  { path: '/orders', element: <OrderListView /> },
  { path: '/inventory_and_manufacturing_picklist', element: <InventoryAndManufacturingList /> },
  { path: '/inventory_picklist_items/:order_id', element: <InventoryPickListItems /> },
];
