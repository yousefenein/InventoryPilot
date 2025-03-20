import { useEffect, useState } from "react";
import { MoonIcon, SunIcon } from "@heroicons/react/24/outline";

export default function ThemeSwitcher() {
    const [theme, setTheme] = useState(
        localStorage.getItem("theme") || "light"
    );

    // Apply theme to <html> tag
    useEffect(() => {
        if (theme === "dark") {
            document.documentElement.classList.add("dark");
        } else {
            document.documentElement.classList.remove("dark");
        }
        localStorage.setItem("theme", theme);
    }, [theme]);

    return (
        <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="flex items-center gap-2 p-2 border rounded-lg bg-gray-200 dark:bg-gray-800"
        >
            {theme === "dark" ? (
                <>
                    <SunIcon className="h-5 w-5 text-yellow-500" />
                    
                </>
            ) : (
                <>
                    <MoonIcon className="h-5 w-5 text-gray-800" />
                   
                </>
            )}
        </button>
    );
}
