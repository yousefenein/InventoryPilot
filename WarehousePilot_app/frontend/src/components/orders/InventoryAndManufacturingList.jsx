import React, { useState } from "react";
import SideBar from "../dashboard_sidebar1/App";
import InventoryPickList from "./InventoyPickList";

const InventoryAndManufacturingList = () => {
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-full">
      <SideBar isOpen={isSidebarOpen} />

      <div className="flex-1 sm:ml-8">

        <InventoryPickList />
      </div>
    </div>
  );
};

export default InventoryAndManufacturingList;
