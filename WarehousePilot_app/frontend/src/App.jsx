import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import routes from "./components/routes";
import { HeroUIProvider } from "@heroui/react";

// Main App Component
function App() {
  const [darkMode, setDarkMode] = useState(false);

  // Check for user's preference on initial load
  useEffect(() => {
    const isDarkMode = localStorage.getItem('dark-mode') === 'true';
    setDarkMode(isDarkMode);
  }, []);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    localStorage.setItem('dark-mode', !darkMode); // Store the preference
  };

  // Modified routes to pass darkMode prop
  const routesWithDarkMode = routes.map(route => ({
    ...route,
    element: React.cloneElement(route.element, { darkMode })
  }));

  return (
    <HeroUIProvider>
    <Router>
    <div className={darkMode ? 'dark bg-gray-900 text-white min-h-screen' : 'bg-white text-black min-h-screen'}>
          {/* Dark mode toggle button */}
          <button onClick={toggleDarkMode} className="p-2 m-4 rounded bg-blue-500 text-white">
            Toggle Dark Mode
          </button>
          
          {/* Routes for the application */}
    
      <Routes>
        
        {/* Map through predefined routes */}
        {routesWithDarkMode.map((route, index) => (
          <Route 
            key={index} 
            path={route.path} 
            element={route.element} 
          />
        ))}
      </Routes>
      </div>
    </Router>
    </HeroUIProvider>
  );
}

export default App;