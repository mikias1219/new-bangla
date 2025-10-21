"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Users,
  CreditCard,
  MessageSquare,
  TrendingUp,
  Shield,
  UserCheck,
  UserX,
  Crown,
  LogOut
} from "lucide-react";

interface AdminStats {
  users: {
    total_users: number;
    active_users: number;
    new_users_today: number;
    new_users_this_week: number;
    new_users_this_month: number;
  };
  subscriptions: {
    total_subscriptions: number;
    active_subscriptions: number;
    trial_subscriptions: number;
    expired_subscriptions: number;
    revenue_this_month: number;
  };
  system: {
    total_conversations: number;
    total_messages: number;
    average_session_duration: number;
    user_satisfaction_rate: number;
  };
}

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  subscription_plan: string | null;
  subscription_status: string | null;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const checkAdminAccess = useCallback(async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        router.push("/login");
        return;
      }

      // Check if user is admin by fetching their profile
      const response = await fetch("/api/users/me", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch user data");
      }

      const userData = await response.json();

      // Check if user is superuser (admin)
      if (!userData.is_superuser) {
        alert("Access denied. Admin privileges required.");
        router.push("/dashboard");
        return;
      }

      // Load admin data
      await loadAdminStats();
      await loadUsers();

    } catch (error) {
      console.error("Admin access check failed:", error);
      router.push("/login");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    checkAdminAccess();
  }, [checkAdminAccess]);

  const loadAdminStats = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("/api/admin/stats", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error("Failed to load admin stats:", error);
    }
  };

  const loadUsers = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("/api/admin/users", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
      console.error("Failed to load users:", error);
    }
  };

  const toggleUserStatus = async (userId: number, isActive: boolean) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/api/admin/users/${userId}/status`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ is_active: isActive }),
      });

      if (response.ok) {
        await loadUsers(); // Refresh user list
        alert(`User ${isActive ? 'activated' : 'deactivated'} successfully`);
      } else {
        alert("Failed to update user status");
      }
    } catch (error) {
      console.error("Failed to toggle user status:", error);
      alert("Failed to update user status");
    }
  };

  const toggleAdminStatus = async (userId: number, isSuperuser: boolean) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/api/admin/users/${userId}/admin`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ is_superuser: isSuperuser }),
      });

      if (response.ok) {
        await loadUsers(); // Refresh user list
        alert(`Admin privileges ${isSuperuser ? 'granted' : 'revoked'} successfully`);
      } else {
        alert("Failed to update admin status");
      }
    } catch (error) {
      console.error("Failed to toggle admin status:", error);
      alert("Failed to update admin status");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
            <div className="flex items-center gap-4">
              <span className="text-gray-700">Administrator</span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <nav className="space-y-2">
                <button
                  onClick={() => setActiveTab("dashboard")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors ${
                    activeTab === "dashboard"
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <TrendingUp className="w-5 h-5" />
                  Dashboard
                </button>
                <button
                  onClick={() => setActiveTab("users")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors ${
                    activeTab === "users"
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <Users className="w-5 h-5" />
                  User Management
                </button>
                <button
                  onClick={() => setActiveTab("subscriptions")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors ${
                    activeTab === "subscriptions"
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <CreditCard className="w-5 h-5" />
                  Subscriptions
                </button>
                <button
                  onClick={() => setActiveTab("system")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors ${
                    activeTab === "system"
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <MessageSquare className="w-5 h-5" />
                  System
                </button>
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {activeTab === "dashboard" && <DashboardOverview stats={stats} />}
            {activeTab === "users" && (
              <UserManagement
                users={users}
                onToggleStatus={toggleUserStatus}
                onToggleAdmin={toggleAdminStatus}
              />
            )}
            {activeTab === "subscriptions" && <SubscriptionManagement />}
            {activeTab === "system" && <SystemManagement />}
          </div>
        </div>
      </div>
    </div>
  );
}

function DashboardOverview({ stats }: { stats: AdminStats | null }) {
  if (!stats) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">Loading dashboard data...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* User Stats */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">User Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-blue-600">Total Users</p>
                <p className="text-2xl font-bold text-blue-900">{stats.users.total_users}</p>
              </div>
            </div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <UserCheck className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-green-600">Active Users</p>
                <p className="text-2xl font-bold text-green-900">{stats.users.active_users}</p>
              </div>
            </div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex items-center">
              <TrendingUp className="w-8 h-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-purple-600">New Today</p>
                <p className="text-2xl font-bold text-purple-900">{stats.users.new_users_today}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Subscription Stats */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Subscription Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-indigo-50 p-4 rounded-lg">
            <div className="flex items-center">
              <CreditCard className="w-8 h-8 text-indigo-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-indigo-600">Active Subscriptions</p>
                <p className="text-2xl font-bold text-indigo-900">{stats.subscriptions.active_subscriptions}</p>
              </div>
            </div>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Shield className="w-8 h-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-yellow-600">Trial Users</p>
                <p className="text-2xl font-bold text-yellow-900">{stats.subscriptions.trial_subscriptions}</p>
              </div>
            </div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Crown className="w-8 h-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-red-600">Revenue (This Month)</p>
                <p className="text-2xl font-bold text-red-900">${stats.subscriptions.revenue_this_month}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function UserManagement({
  users,
  onToggleStatus,
  onToggleAdmin
}: {
  users: User[];
  onToggleStatus: (userId: number, isActive: boolean) => void;
  onToggleAdmin: (userId: number, isSuperuser: boolean) => void;
}) {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">User Management</h2>
        <p className="text-gray-600">Manage user accounts and permissions</p>
      </div>
      <div className="p-6">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Plan
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {user.full_name || user.username}
                        </div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                      {user.is_superuser && (
                        <Crown className="w-4 h-4 text-yellow-500 ml-2" />
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.subscription_plan || 'None'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      onClick={() => onToggleStatus(user.id, !user.is_active)}
                      className={`inline-flex items-center px-3 py-1 rounded-md text-sm font-medium ${
                        user.is_active
                          ? 'bg-red-100 text-red-700 hover:bg-red-200'
                          : 'bg-green-100 text-green-700 hover:bg-green-200'
                      }`}
                    >
                      {user.is_active ? <UserX className="w-4 h-4 mr-1" /> : <UserCheck className="w-4 h-4 mr-1" />}
                      {user.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                    {!user.is_superuser && (
                      <button
                        onClick={() => onToggleAdmin(user.id, true)}
                        className="inline-flex items-center px-3 py-1 rounded-md text-sm font-medium bg-yellow-100 text-yellow-700 hover:bg-yellow-200"
                      >
                        <Shield className="w-4 h-4 mr-1" />
                        Make Admin
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function SubscriptionManagement() {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Subscription Management</h2>
      <p className="text-gray-600">Manage subscription plans and billing</p>
      <div className="mt-6">
        <p className="text-gray-500">Subscription management features will be available soon.</p>
      </div>
    </div>
  );
}

function SystemManagement() {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">System Management</h2>
      <p className="text-gray-600">Monitor system performance and logs</p>
      <div className="mt-6">
        <p className="text-gray-500">System management features will be available soon.</p>
      </div>
    </div>
  );
}
