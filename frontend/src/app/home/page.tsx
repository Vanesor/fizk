// app/(authenticated)/home/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  HomeIcon,
  ArrowLeftOnRectangleIcon,
  ArrowPathIcon,
} from "@heroicons/react/24/solid";
import Link from "next/link";

// Implement proper logging helper
type LogPayload =
  | string
  | number
  | boolean
  | Record<string, unknown>
  | null
  | undefined;
const log = {
  info: (message: string, ...args: LogPayload[]) =>
    console.log("[INFO]", message, ...args),
  debug: (message: string, ...args: LogPayload[]) =>
    console.debug("[DEBUG]", message, ...args),
  error: (message: string, ...args: LogPayload[]) =>
    console.error("[ERROR]", message, ...args),
  warn: (message: string, ...args: LogPayload[]) =>
    console.warn("[WARN]", message, ...args),
};

// Placeholder auth check
const checkAuthStatus = () => {
  log.debug("Placeholder: Checking auth status.");
  // Replace with actual token/session check
  // Example: return !!localStorage.getItem('authToken');
  return true; // Assume authenticated for demo
};

export default function HomePage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    log.info("Home page mounted, checking authentication.");
    const authStatus = checkAuthStatus();
    setIsAuthenticated(authStatus);
    if (!authStatus) {
      log.warn("User not authenticated, redirecting to login.");
      router.replace("/"); // Redirect to login page ('/')
    } else {
      log.info("User authenticated.");
    }
  }, [router]);

  const handleLogout = () => {
    log.info("Logout initiated.");
    // --- TODO: Clear Auth Token/Session ---
    // Example: localStorage.removeItem('authToken');
    // ------------------------------------
    setIsAuthenticated(false); // Update state
    router.replace("/"); // Redirect to login page after logout
  };

  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <ArrowPathIcon className="animate-spin h-10 w-10 text-blue-500" />
        <span className="ml-3 text-lg">Checking authentication...</span>
      </div>
    );
  }

  // This part should ideally not be reached if redirect works, but good fallback
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-center p-6">
        <p className="text-xl text-red-600 dark:text-red-400 mb-4">
          Access Denied
        </p>
        <Link href="/" className="text-blue-600 hover:underline">
          Please Login
        </Link>
      </div>
    );
  }

  // Authenticated View
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-md">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <HomeIcon className="h-8 w-8 text-blue-600 dark:text-blue-400" />
              <span className="ml-3 font-bold text-xl">Dashboard</span>
            </div>
            <div>
              <button onClick={handleLogout} className="...">
                {" "}
                <ArrowLeftOnRectangleIcon className="h-5 w-5 mr-2" /> Logout{" "}
              </button>
            </div>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <motion.div
          className="..."
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl font-semibold mb-4">Welcome!</h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            {" "}
            You have successfully authenticated using Zero-Knowledge Proofs.{" "}
          </p>
          {/* ... More dashboard content ... */}
        </motion.div>
      </main>
    </div>
  );
}
