import type { NavbarProps } from "@nextui-org/react";
import { useNavigate, useLocation } from 'react-router-dom';
import React from "react";
import {
  Navbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  NavbarMenu,
  NavbarMenuItem,
  NavbarMenuToggle,
  Link,
  Button,
} from "@nextui-org/react";

export default function NavBar(props: NavbarProps) {
  const navigate = useNavigate();
  const location = useLocation();

  // Retrieve user info from localStorage
  const user = localStorage.getItem("user");
  const parsedUser = user ? JSON.parse(user) : null;
  const userRole = parsedUser ? parsedUser.role : null;

  const handleLoginAsDifferentUser = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <Navbar
      {...props}
      classNames={{
        base: "py-4 backdrop-filter-none bg-transparent",
        wrapper: "px-0 w-full justify-center bg-transparent",
        item: "hidden md:flex",
      }}
      height="54px"
    >
      <NavbarContent
        className="gap-4 rounded-full border-small border-default-200/20 bg-background/60 px-2 shadow-medium backdrop-blur-md backdrop-saturate-150 dark:bg-default-100/50"
        justify="center"
      >
        {/* Toggle for mobile */}
        <NavbarMenuToggle className="ml-2 text-default-400 md:hidden" />

        {/* Logo */}
        <NavbarBrand className="mr-2 w-[40vw] md:w-auto md:max-w-fit">
          <div className="rounded-full bg-foreground text-background">
            {/* <csfLogo size={34} /> */}
          </div>
          <span className="ml-2 font-medium md:hidden">CSF</span>
        </NavbarBrand>

        {/* Conditionally Rendered Navbar Items */}
        <NavbarItem>
          <Link className="text-default-500" href="/dashboard" size="sm">
            Home
          </Link>
        </NavbarItem>

        {(userRole === "admin" || userRole === "manager") && (
          <>
            <NavbarItem>
              <Link className="text-default-500" href="/kpi" size="sm">
                KPI
              </Link>
            </NavbarItem>
            <NavbarItem>
              <Link className="text-default-500" href="/orders" size="sm">
                Orders
              </Link>
            </NavbarItem>
            <NavbarItem>
              <Link className="text-default-500" href="/inventory-stock" size="sm">
                Inventory
              </Link>
            </NavbarItem>
            <NavbarItem>
              <Link className="text-default-500" href="/manufacturing_tasks" size="sm">
              Manufacturing Tasks
              </Link>
            </NavbarItem>
          </>
        )}

        {userRole === "staff" && (
          <NavbarItem>
            <Link className="text-default-500" href="/staff_manufacturing_tasks" size="sm">
              My Tasks
            </Link>
          </NavbarItem>
        )}

        {userRole === "qa" && (
          <>
            <NavbarItem>
              <Link className="text-default-500" href="/qa_tasks" size="sm">
                QA Tasks
              </Link>
            </NavbarItem>
            <NavbarItem>
              <Link className="text-default-500" href="/qa_error_list_view" size="sm">
                Error Reports
              </Link>
            </NavbarItem>
          </>
        )}

        {/* Common item for all logged-in users */}
        {userRole && (
          <NavbarItem>
            <Link className="text-default-500" href="/account_management" size="sm">
              Account
            </Link>
          </NavbarItem>
        )}

        {/* Login/Logout Button */}
        <NavbarItem className="ml-2 !flex">
          {userRole ? (
            <Button radius="full" variant="flat" onPress={handleLoginAsDifferentUser}>
              Logout
            </Button>
          ) : (
            <Button radius="full" variant="flat" onPress={() => navigate("/login")}>
              Login
            </Button>
          )}
        </NavbarItem>
      </NavbarContent>

      {/* Mobile Menu */}
      <NavbarMenu
        className="top-[calc(var(--navbar-height)/2)] mx-auto mt-16 max-h-[40vh] max-w-[80vw] rounded-large border-small border-default-200/20 bg-background/60 py-6 shadow-medium backdrop-blur-md backdrop-saturate-150 dark:bg-default-100/50"
        motionProps={{
          initial: { opacity: 0, y: -20 },
          animate: { opacity: 1, y: 0 },
          exit: { opacity: 0, y: -20 },
          transition: {
            ease: "easeInOut",
            duration: 0.2,
          },
        }}
      >
        {/* Dynamically render menu items based on role */}
        {userRole === "admin" || userRole === "manager" ? (
          <>
            <NavbarMenuItem>
              <Link href="/kpi">KPI</Link>
            </NavbarMenuItem>
            <NavbarMenuItem>
              <Link href="/orders">Orders</Link>
            </NavbarMenuItem>
            <NavbarMenuItem>
              <Link href="/inventory-stock">Inventory</Link>
            </NavbarMenuItem>
          </>
        ) : userRole === "staff" ? (
          <NavbarMenuItem>
            <Link href="/staff_manufacturing_tasks">My Tasks</Link>
          </NavbarMenuItem>
        ) : userRole === "qa" ? (
          <>
            <NavbarMenuItem>
              <Link href="/qa_tasks">QA Tasks</Link>
            </NavbarMenuItem>
            <NavbarMenuItem>
              <Link href="/qa_error_list_view">Error Reports</Link>
            </NavbarMenuItem>
          </>
        ) : null}

        {userRole && (
          <NavbarMenuItem>
            <Link href="/account_management">Account</Link>
          </NavbarMenuItem>
        )}

        <NavbarMenuItem>
          {userRole ? (
            <Button variant="light" onPress={handleLoginAsDifferentUser}>
              Logout
            </Button>
          ) : (
            <Button variant="light" onPress={() => navigate("/login")}>
              Login
            </Button>
          )}
        </NavbarMenuItem>
      </NavbarMenu>
    </Navbar>
  );
}
