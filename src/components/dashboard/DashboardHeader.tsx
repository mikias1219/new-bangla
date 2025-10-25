"use client";

import { useState } from "react";
import {
  Sun,
  Moon,
  Bell,
  User,
  Menu,
  LogOut
} from "lucide-react";

interface DashboardHeaderProps {
  onSidebarToggle: () => void;
  sidebarCollapsed: boolean;
}

export default function DashboardHeader({ onSidebarToggle, sidebarCollapsed }: DashboardHeaderProps) {
  const [darkMode, setDarkMode] = useState(false);
  const [notifications] = useState(3); // Mock notification count

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    // In a real app, this would update the theme globally
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 h-16 fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6">
      {/* Left side - Logo and Sidebar Toggle */}
      <div className="flex items-center gap-4">
        <button
          onClick={onSidebarToggle}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors md:hidden"
          title="Toggle Sidebar"
        >
          <Menu className="w-5 h-5 text-gray-600" />
        </button>

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center shadow-sm">
            <span className="text-white font-bold text-sm">B</span>
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">BanglaChatPro</h1>
            <p className="text-xs text-gray-500 hidden sm:block">AI Customer Service Platform</p>
          </div>
        </div>
      </div>

      {/* Right side - Actions */}
      <div className="flex items-center gap-4">
        {/* Theme Toggle */}
        <button
          onClick={toggleDarkMode}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
        >
          {darkMode ? (
            <Sun className="w-5 h-5 text-gray-600" />
          ) : (
            <Moon className="w-5 h-5 text-gray-600" />
          )}
        </button>

        {/* Notifications */}
        <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors relative">
          <Bell className="w-5 h-5 text-gray-600" />
          {notifications > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
              {notifications}
            </span>
          )}
        </button>

        {/* User Avatar */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center shadow-sm">
            <User className="w-4 h-4 text-white" />
          </div>
          <div className="hidden md:block">
            <p className="text-sm font-medium text-gray-900">Admin User</p>
            <p className="text-xs text-gray-500">Platform Administrator</p>
          </div>
        </div>

        {/* Logout Button */}
        <button
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-600 hover:text-gray-900"
          title="Logout"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
}
