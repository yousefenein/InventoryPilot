import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import routes from "./components/routes";  
import { HeroUIProvider } from "@heroui/react";

// Main App Component
function App() {
  return (
    <Router>
      <HeroUIProvider>
      <Routes>
        
        {/* Map through predefined routes */}
        {routes.map((route, index) => (
          <Route 
            key={index} 
            path={route.path} 
            element={route.element} 
          />
        ))}
      </Routes>
      </HeroUIProvider>
    </Router>
  );
}

export default App;
