"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import DashboardSidebar from "@/components/dashboard/DashboardSidebar";
import DashboardHeader from "@/components/dashboard/DashboardHeader";
import AgentManagementPage from "@/components/dashboard/AgentManagementPage";
import SystemSettingsPage from "@/components/dashboard/SystemSettingsPage";
import DashboardBreadcrumb from "@/components/dashboard/DashboardBreadcrumb";

interface AIAgent {
  id: number;
  name: string;
  description: string;
  whatsapp_enabled: boolean;
  facebook_enabled: boolean;
  total_conversations: number;
  training_status: string;
}

interface TrainingDocument {
  id: number;
  filename: string;
  status: string;
  word_count: number;
  uploaded_at: string;
  trained_at: string | null;
}

interface Organization {
  id: number;
  name: string;
  domain: string;
  plan: string;
  max_users: number;
  max_ai_agents: number;
  max_monthly_chats: number;
  current_monthly_chats: number;
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Mock authentication check - in real app, check token
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    setLoading(false);
  }, []);

  const handleSidebarToggle = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Fixed Header */}
      <DashboardHeader
        onSidebarToggle={handleSidebarToggle}
        sidebarCollapsed={sidebarCollapsed}
      />

      <div className="flex">
        {/* Fixed Sidebar */}
        <DashboardSidebar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          isCollapsed={sidebarCollapsed}
          onToggleCollapse={handleSidebarToggle}
        />

        {/* Main Content Area */}
        <div className={`flex-1 transition-all duration-300 ${sidebarCollapsed ? 'ml-16' : 'ml-64'}`}>
          <div className="min-h-screen">
            {activeTab === "dashboard" && (
              <div className="p-6">
                <DashboardBreadcrumb items={[{ label: "Dashboard" }]} />

                <div className="mt-6">
                  <h1 className="text-2xl font-bold text-gray-900 mb-2">Dashboard Overview</h1>
                  <p className="text-gray-600">Welcome to your BanglaChatPro dashboard</p>
                </div>

                {/* Dashboard Content Placeholder */}
                <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-white text-2xl font-bold">B</span>
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Dashboard Overview</h3>
                    <p className="text-gray-600 mb-6">Performance overview and key metrics will be displayed here.</p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
                      <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600 mb-2">156</div>
                        <div className="text-sm text-blue-700">Total Users</div>
                      </div>
                      <div className="bg-gradient-to-r from-green-50 to-green-100 p-6 rounded-lg">
                        <div className="text-2xl font-bold text-green-600 mb-2">23</div>
                        <div className="text-sm text-green-700">Active Organizations</div>
                      </div>
                      <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-6 rounded-lg">
                        <div className="text-2xl font-bold text-purple-600 mb-2">89</div>
                        <div className="text-sm text-purple-700">AI Agents</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "conversations-log" && (
              <div className="p-6">
                <DashboardBreadcrumb items={[{ label: "Dashboard" }, { label: "Conversations Log" }]} />

                <div className="mt-6">
                  <h1 className="text-2xl font-bold text-gray-900 mb-2">Conversations Log</h1>
                  <p className="text-gray-600">Monitor and audit all customer conversations</p>
                </div>

                <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                  <div className="text-center py-12">
                    <p className="text-gray-600">Conversations log functionality will be implemented here</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "agent-management" && (
              <AgentManagementPage />
            )}

            {activeTab === "intents-training" && (
              <div className="p-6">
                <DashboardBreadcrumb items={[{ label: "Dashboard" }, { label: "Intents & Training" }]} />

                <div className="mt-6">
                  <h1 className="text-2xl font-bold text-gray-900 mb-2">Intents & Training</h1>
                  <p className="text-gray-600">Manage conversation intents and continuous learning</p>
                </div>

                <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                  <div className="text-center py-12">
                    <p className="text-gray-600">Intents and training management will be implemented here</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "system-settings" && (
              <SystemSettingsPage />
            )}

            {activeTab === "analytics-reports" && (
              <div className="p-6">
                <DashboardBreadcrumb items={[{ label: "Dashboard" }, { label: "Analytics & Reports" }]} />

                <div className="mt-6">
                  <h1 className="text-2xl font-bold text-gray-900 mb-2">Analytics & Reports</h1>
                  <p className="text-gray-600">View performance data and detailed reports</p>
                </div>

                <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                  <div className="text-center py-12">
                    <p className="text-gray-600">Analytics and reporting features will be implemented here</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "review-ratings" && (
              <div className="p-6">
                <DashboardBreadcrumb items={[{ label: "Dashboard" }, { label: "Review & Ratings" }]} />

                <div className="mt-6">
                  <h1 className="text-2xl font-bold text-gray-900 mb-2">Review & Ratings</h1>
                  <p className="text-gray-600">Monitor customer satisfaction and feedback</p>
                </div>

                <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                  <div className="text-center py-12">
                    <p className="text-gray-600">Review and ratings functionality will be implemented here</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "security-logs" && (
              <div className="p-6">
                <DashboardBreadcrumb items={[{ label: "Dashboard" }, { label: "Security & Logs" }]} />

                <div className="mt-6">
                  <h1 className="text-2xl font-bold text-gray-900 mb-2">Security & Logs</h1>
                  <p className="text-gray-600">PII masking and compliance audit logs</p>
                </div>

                <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                  <div className="text-center py-12">
                    <p className="text-gray-600">Security and logging features will be implemented here</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}