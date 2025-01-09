import { Dashboard, ManagerDashboard, AdminDashboard, AccountManagement, ChangePassword, Profile  } from '../dashboard';
import KpiDashboard from "../dashboard/KpiDashboard"
import InventoryTable from '../inventory-stock/App'; 
import ManageUsersPage from '../admin_manage_users/ManageUsersPage';
import AddUsersDashboard from '../dashboard/AddUsersDashboard';
import NotifCard from '../notifications/notifications-card/App';
import NavBar from '../navbar/App';
import OrderListView from '../orders/OrderListView'; 
import ManageUsersTable from '../admin_manage_users/manage_users_table/App';
import InventoyPickList from '../orders/InventoyPickList';
import InventoryPickListItems from '../orders/InventoryPickListItems';
import { chip } from '@nextui-org/react';


export const dashboard_routes = [
  { path: '/dashboard', element: <Dashboard /> },
  { path: '/manager_dashboard', element: <ManagerDashboard /> },

  { path: '/admin_dashboard', element: <AdminDashboard />, 
    children: [ 
      { path: 'manage_users', element: <ManageUsersTable /> },
      { path: 'add_users', element: <AddUsersDashboard />},
      { path: 'edit_user/:user_id', element: <AddUsersDashboard />}
    ]
   },
  
  { path: '/account_management', element: <AccountManagement /> },
  { path: '/profile', element: <Profile /> },
  { path: '/kpi', element: <KpiDashboard /> },
  { path: '/change_password', element: <ChangePassword /> },
  { path: '/inventory-stock', element: <InventoryTable /> },
  // {path: '/admin_dashboard/add_users', element: <AddUsersDashboard />}, duplicate to be removed
  { path: '/navbar', element: <NavBar /> },
  { path: '/orders', element: <OrderListView /> },
  { path: '/inventory_pick_list', element: <InventoyPickList /> },
  { path: '/inventory_picklist_items/:order_id', element: <InventoryPickListItems /> },
];
