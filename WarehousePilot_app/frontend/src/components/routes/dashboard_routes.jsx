import ProtectedRoute from "./protected_routes";
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


export const dashboard_routes = [
  { path: '/dashboard', element: (
    <>
      <ProtectedRoute allowedRoles={['admin', 'manager', 'staff']} />
      <Dashboard /> 
    </> 
  ) },
  { path: '/manager_dashboard', element: (
    <>
      <ProtectedRoute allowedRoles={['admin', 'manager']} />
      <ManagerDashboard />
    </>
  ) },
  { path: '/admin_dashboard', element: (
    <>
      <ProtectedRoute allowedRoles={['admin']} />
      <AdminDashboard /> 
    </> 
  ) },
  { path: '/admin_dashboard/manage_users', element: (
      <>
        <ProtectedRoute allowedRoles={['admin']} />
        <ManageUsersTable />
      </>
  ) },
  { path: '/account_management', element: (
      <>
        <ProtectedRoute allowedRoles={['admin', 'manager', 'staff', 'qa']} />
        <AccountManagement />
      </>
  ) },
  { path: '/profile', element: (
      <>
        <ProtectedRoute allowedRoles={['admin', 'manager', 'staff', 'qa']} />
        <Profile />
      </>
  ) },
  { path: '/kpi', element: (
      <>
        <ProtectedRoute allowedRoles={['admin', 'manager']} />
        <KpiDashboard />
      </>
  ) },
  { path: '/change_password', element: (
      <>
        <ProtectedRoute allowedRoles={['admin', 'manager', 'staff', 'qa']} />
        <ChangePassword />
      </>
  ) },
  { path: '/inventory-stock', element: (
      <>
        <ProtectedRoute allowedRoles={['admin', 'manager', 'staff']} />
        <InventoryTable />
      </>
  ) },
  { path: '/admin_dashboard/add_users', element: (
      <>
        <ProtectedRoute allowedRoles={['admin']} />
        <AddUsersDashboard />
      </>
  ) },
  { path: '/navbar', element: (
      <>
        <ProtectedRoute allowedRoles={['admin', 'manager', 'staff', 'qa']} />
        <NavBar />
      </>
  ) },
  { path: '/admin_dashboard/edit_user/:user_id', element: (
      <>
        <ProtectedRoute allowedRoles={['admin']} />
        <AddUsersDashboard />
      </>
  ) },
  { path: '/orders', element: (
      <>
        <ProtectedRoute allowedRoles={['admin', 'manager', 'staff']} />
        <OrderListView />
      </>
  ) },
  { path: '/inventory_pick_list', element: (
      <>
        <ProtectedRoute allowedRoles={['admin', 'manager', 'staff']} />
        <InventoyPickList />
      </>
  ) },
  { path: '/staff_dashboard', element: (
      <>
        <ProtectedRoute allowedRoles={['staff']} />
        <StaffDashboard />
      </>
  ) },
  { path: '/assigned_picklist', element: (
      <>
        <ProtectedRoute allowedRoles={['staff']} />
        <AssignedPickList />
      </>
  ) },
  { path: '/inventory_and_manufacturing_picklist', element: (
      <>
        <ProtectedRoute allowedRoles={['admin', 'manager']} />
        <InventoryAndManufacturingList />
      </>
  ) },
  { path: '/inventory_picklist_items/:order_id', element: (
      <>
        <ProtectedRoute allowedRoles={['admin', 'manager', 'staff']} />
        <InventoryPickListItem />
      </>
  ) },
  { path: '/qa_dashboard', element: (
      <>
        <ProtectedRoute allowedRoles={['qa']} />
        <QADashboard />
      </>
  ) },
  { path: '/manufacturing_list_item/:order_id', element: (
      <>
        <ProtectedRoute allowedRoles={['admin', 'manager']} />
        <ManufacturingListItem />
      </>
  ) },
  { path: '/qa_tasks', element: (
      <>
        <ProtectedRoute allowedRoles={['qa']} />
        <QATasks />
      </>
  ) }
];
