import { Dashboard, ManagerDashboard, AdminDashboard, AccountManagement, ChangePassword, Profile, StaffDashboard, QADashboard  } from '../dashboard';
import KpiDashboard from "../dashboard/KpiDashboard"
import InventoryTable from '../inventory-stock/App'; 
import ManageUsersPage from '../admin_manage_users/ManageUsersPage';
import AddUsersDashboard from '../dashboard/AddUsersDashboard';
import NotifCard from '../notifications/notifications-card/App';
import NavBar from '../navbar/App';
import OrderListView from '../orders/OrderListView'; 
import ManageUsersTable from '../admin_manage_users/manage_users_table/App';
import InventoyPickList from '../orders/InventoyPickList';
import AssignedPickList from '../orders/AssignedPickList';
import InventoryPickListItem from '../orders/InventoryPickListItem';
import InventoryAndManufacturingList from '../orders/InventoryAndManufacturingList';
import ManufacturingListItem from '../orders/ManufacturingListItem';
import QATasks from '../orders/QAtasks';
import StaffManufacturingTasks from '../manufacturing/StaffManufacturingTasks';
import ManuTasksTable from '../manufacturing/ManufacturingTasks/manu-tasks/App';

import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ element }) => {
  const isLoggedIn = !!localStorage.getItem('token');
  return isLoggedIn ? element : <Navigate to="/" />;
};

export const dashboard_routes = [
  { path: '/dashboard', element: <ProtectedRoute element={<Dashboard />} /> },
  { path: '/manager_dashboard', element:  <ProtectedRoute element={<ManagerDashboard />} /> },
  { path: '/admin_dashboard', element:  <ProtectedRoute element={<AdminDashboard />} /> },
  { path: '/admin_dashboard/manage_users', element: <ProtectedRoute element={<ManageUsersPage />} /> },
  { path: '/account_management', element: <ProtectedRoute element={<AccountManagement />} /> },
  { path: '/profile', element: <ProtectedRoute element={<Profile />} /> },
  { path: '/kpi', element: <ProtectedRoute element={<KpiDashboard />} /> },
  { path: '/change_password', element: <ProtectedRoute element={<ChangePassword />} /> },
  { path: '/inventory-stock', element: <ProtectedRoute element={<InventoryTable />} /> },
  { path: '/admin_dashboard/add_users', element: <ProtectedRoute element={<AddUsersDashboard />} /> },
  { path: '/admin_dashboard/edit_user/:user_id', element: <ProtectedRoute element={<AddUsersDashboard />} /> },
  { path: '/admin_dashboard/add_users', element: <AddUsersDashboard />},
  { path: '/orders', element: <OrderListView /> },
  { path: '/inventory_pick_list', element: <InventoyPickList /> },
  { path: '/staff_dashboard', element: <StaffDashboard /> },
  { path: '/assigned_picklist', element: <AssignedPickList /> },
  { path: '/inventory_and_manufacturing_picklist', element: <InventoryAndManufacturingList /> },
  { path: '/inventory_picklist_items/:order_id', element: <InventoryPickListItem /> },
  { path: '/qa_dashboard', element: <QADashboard/> },
  { path: '/manufacturing_list_item/:order_id', element: <ManufacturingListItem /> },
  { path: '/qa_tasks', element: <QATasks /> },
  { path: '/manufacturing_list_item/:order_id', element: <ManufacturingListItem /> },
  { path: '/staff_manufacturing_tasks', element: <StaffManufacturingTasks /> }, 
  { path: '/manufacturing_tasks', element: <ManuTasksTable /> },

];

