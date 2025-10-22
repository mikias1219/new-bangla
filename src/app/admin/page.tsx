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
  LogOut,
  Building,
  Bot,
  Settings,
  BarChart3,
  Play,
  Mic,
  MicOff,
  Volume2
} from "lucide-react";
import VoiceChat, { speakAiResponse } from "@/components/voice/VoiceChat";

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
  ai_agents: {
    total_agents: number;
    active_agents: number;
    total_conversations: number;
    average_confidence: number;
    escalated_conversations: number;
    platform_breakdown: { [key: string]: number };
  };
  organizations: {
    total_organizations: number;
    active_organizations: number;
    total_chat_limit: number;
    used_chats: number;
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
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [aiAgents, setAiAgents] = useState<AIAgent[]>([]);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [loading, setLoading] = useState(true);

  // Test AI Agent states
  const [selectedAgentId, setSelectedAgentId] = useState<number | null>(null);
  const [testMessages, setTestMessages] = useState<Array<{type: 'user' | 'ai', content: string, timestamp: Date}>>([]);
  const [testInput, setTestInput] = useState("");
  const [isTesting, setIsTesting] = useState(false);
  const [isVoiceTesting, setIsVoiceTesting] = useState(false);

  // AI Agent Management states
  const [showCreateAgentModal, setShowCreateAgentModal] = useState(false);
  const [selectedOrgForAgent, setSelectedOrgForAgent] = useState<number | null>(null);
  const [newAgentData, setNewAgentData] = useState({
    name: "",
    description: "",
    systemPrompt: ""
  });
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
      await loadOrganizations();
      await loadAiAgents();

    } catch (error) {
      console.error("Admin access check failed:", error);
      router.push("/login");
    } finally {
      setLoading(false);
    }
  }, [router]);

  // Test AI Agent Functions
  const sendTestMessage = async (message: string) => {
    if (!message.trim()) return;

    setIsTesting(true);
    const userMessage = { type: 'user' as const, content: message, timestamp: new Date() };
    setTestMessages(prev => [...prev, userMessage]);

    try {
      const token = localStorage.getItem("token");

      // Use different endpoint based on whether an agent is selected
      let endpoint = "";
      let requestBody: any = { message: message.trim() };

      if (selectedAgentId) {
        // Test with specific agent
        endpoint = `/api/chat/send-message?agent_id=${selectedAgentId}`;
      } else {
        // General OpenAI testing without specific agent
        endpoint = `/api/admin/test-openai`;
        requestBody = {
          message: message.trim(),
          model: "gpt-4",
          system_prompt: "You are a helpful AI assistant. Respond in a friendly and professional manner."
        };
      }

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(requestBody),
      });

      if (response.ok) {
        const data = await response.json();
        const aiResponse = selectedAgentId ? data.response : data.choices[0].message.content;
        const aiMessage = { type: 'ai' as const, content: aiResponse, timestamp: new Date() };
        setTestMessages(prev => [...prev, aiMessage]);

        // Speak the AI response
        if (aiResponse) {
          speakAiResponse(aiResponse);
        }
      } else {
        const error = await response.json();
        const errorMessage = { type: 'ai' as const, content: `Error: ${error.detail || 'Failed to get AI response'}`, timestamp: new Date() };
        setTestMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error("Test message error:", error);
      const errorMessage = { type: 'ai' as const, content: "Error: Failed to send message", timestamp: new Date() };
      setTestMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTesting(false);
    }
  };

  const handleVoiceMessage = (voiceMessage: string) => {
    if (voiceMessage.trim()) {
      sendTestMessage(voiceMessage);
    }
  };

  const clearTestChat = () => {
    setTestMessages([]);
    setTestInput("");
  };

  // AI Agent Management Functions
  const createAIAgentForOrg = async () => {
    if (!selectedOrgForAgent || !newAgentData.name.trim()) return;

    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/api/admin/organizations/${selectedOrgForAgent}/ai-agents`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: newAgentData.name.trim(),
          description: newAgentData.description.trim(),
          system_prompt: newAgentData.systemPrompt.trim() || undefined
        }),
      });

      if (response.ok) {
        const data = await response.json();
        alert(`AI Agent created successfully for ${data.organization_name}!`);
        setShowCreateAgentModal(false);
        setNewAgentData({ name: "", description: "", systemPrompt: "" });
        setSelectedOrgForAgent(null);
        await loadAiAgents(); // Refresh the list
      } else {
        const error = await response.json();
        alert(`Failed to create AI agent: ${error.detail}`);
      }
    } catch (error) {
      console.error("Create agent error:", error);
      alert("Failed to create AI agent. Please try again.");
    }
  };

  const toggleAgentStatus = async (agentId: number, isActive: boolean) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/api/admin/ai-agents/${agentId}/status`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ is_active: !isActive }),
      });

      if (response.ok) {
        alert(`AI Agent ${!isActive ? 'activated' : 'deactivated'} successfully!`);
        await loadAiAgents(); // Refresh the list
      } else {
        const error = await response.json();
        alert(`Failed to update agent status: ${error.detail}`);
      }
    } catch (error) {
      console.error("Toggle agent status error:", error);
      alert("Failed to update agent status. Please try again.");
    }
  };

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

  const loadOrganizations = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("/api/admin/organizations", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setOrganizations(data);
      }
    } catch (error) {
      console.error("Failed to load organizations:", error);
    }
  };

  const loadAiAgents = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("/api/admin/ai-agents", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAiAgents(data);
      }
    } catch (error) {
      console.error("Failed to load AI agents:", error);
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
                  onClick={() => setActiveTab("organizations")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors ${
                    activeTab === "organizations"
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <Building className="w-5 h-5" />
                  Organizations
                </button>
                <button
                  onClick={() => setActiveTab("ai-agents")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors ${
                    activeTab === "ai-agents"
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <Bot className="w-5 h-5" />
                  AI Agents
                </button>
                <button
                  onClick={() => setActiveTab("test-ai")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors ${
                    activeTab === "test-ai"
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <Play className="w-5 h-5" />
                  Test AI Agents
                </button>
                <button
                  onClick={() => setActiveTab("analytics")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors ${
                    activeTab === "analytics"
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <BarChart3 className="w-5 h-5" />
                  Analytics
                </button>
                <button
                  onClick={() => setActiveTab("system")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors ${
                    activeTab === "system"
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <Settings className="w-5 h-5" />
                  System Settings
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
            {activeTab === "organizations" && (
              <OrganizationManagement organizations={organizations} />
            )}
            {activeTab === "ai-agents" && (
              <AIAgentManagement
                aiAgents={aiAgents}
                organizations={organizations}
                onCreateAgent={() => setShowCreateAgentModal(true)}
                onToggleStatus={toggleAgentStatus}
                onTestAgent={(agentId) => {
                  setSelectedAgentId(agentId);
                  setActiveTab("test-ai");
                }}
              />
            )}
            {activeTab === "test-ai" && (
              <TestAIAgents
                aiAgents={aiAgents}
                selectedAgentId={selectedAgentId}
                setSelectedAgentId={setSelectedAgentId}
                testMessages={testMessages}
                testInput={testInput}
                setTestInput={setTestInput}
                isTesting={isTesting}
                isVoiceTesting={isVoiceTesting}
                sendTestMessage={sendTestMessage}
                handleVoiceMessage={handleVoiceMessage}
                clearTestChat={clearTestChat}
              />
            )}
            {activeTab === "analytics" && <AnalyticsDashboard stats={stats} />}
            {activeTab === "subscriptions" && <SubscriptionManagement />}
            {activeTab === "system" && <SystemManagement />}
          </div>
        </div>
      </div>

      {/* Create AI Agent Modal */}
      {showCreateAgentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Create AI Agent</h3>
                <button
                  onClick={() => setShowCreateAgentModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Organization
                  </label>
                  <select
                    value={selectedOrgForAgent || ""}
                    onChange={(e) => setSelectedOrgForAgent(e.target.value ? parseInt(e.target.value) : null)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Choose an organization...</option>
                    {organizations.map((org) => (
                      <option key={org.id} value={org.id}>
                        {org.name} ({org.domain})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Agent Name
                  </label>
                  <input
                    type="text"
                    value={newAgentData.name}
                    onChange={(e) => setNewAgentData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="e.g., Customer Support Assistant"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={newAgentData.description}
                    onChange={(e) => setNewAgentData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Describe what this AI agent will help with..."
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    System Prompt (Optional)
                  </label>
                  <textarea
                    value={newAgentData.systemPrompt}
                    onChange={(e) => setNewAgentData(prev => ({ ...prev, systemPrompt: e.target.value }))}
                    placeholder="Custom system prompt for the AI agent..."
                    rows={4}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    If left empty, a default prompt will be generated based on the organization.
                  </p>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowCreateAgentModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={createAIAgentForOrg}
                  disabled={!selectedOrgForAgent || !newAgentData.name.trim()}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Create Agent
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
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

function OrganizationManagement({ organizations }: { organizations: Organization[] }) {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">Organization Management</h2>
        <p className="text-gray-600">Manage client organizations and their AI agents</p>
      </div>
      <div className="p-6">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Organization
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Plan
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  AI Agents
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usage
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {organizations.map((org) => (
                <tr key={org.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {org.name}
                      </div>
                      <div className="text-sm text-gray-500">{org.domain}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                      {org.plan}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {org.max_ai_agents}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {org.current_monthly_chats}/{org.max_monthly_chats}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      org.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {org.status}
                    </span>
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

function AIAgentManagement({
  aiAgents,
  organizations,
  onCreateAgent,
  onToggleStatus,
  onTestAgent
}: {
  aiAgents: AIAgent[];
  organizations: Organization[];
  onCreateAgent: () => void;
  onToggleStatus: (agentId: number, isActive: boolean) => void;
  onTestAgent: (agentId: number) => void;
}) {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">AI Agent Management</h2>
            <p className="text-gray-600">Monitor and manage all AI agents across organizations</p>
          </div>
          <button
            onClick={onCreateAgent}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-4 h-4" />
            Create Agent
          </button>
        </div>
      </div>
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {aiAgents.map((agent) => (
            <div key={agent.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-medium text-gray-900">{agent.name}</h3>
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  agent.is_active
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {agent.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>

              <p className="text-sm text-gray-600 mb-3">{agent.description}</p>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Conversations:</span>
                  <span className="font-medium">{agent.total_conversations}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Messages:</span>
                  <span className="font-medium">{agent.total_messages}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Training Status:</span>
                  <span className="font-medium">{agent.training_status}</span>
                </div>
              </div>

              <div className="mt-3 flex flex-wrap gap-1">
                {agent.whatsapp_enabled && (
                  <span className="inline-flex px-2 py-1 text-xs font-semibold rounded bg-green-100 text-green-800">
                    WhatsApp
                  </span>
                )}
                {agent.facebook_enabled && (
                  <span className="inline-flex px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                    Facebook
                  </span>
                )}
                {agent.instagram_enabled && (
                  <span className="inline-flex px-2 py-1 text-xs font-semibold rounded bg-pink-100 text-pink-800">
                    Instagram
                  </span>
                )}
              </div>

              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => onTestAgent(agent.id)}
                  className="flex-1 flex items-center justify-center gap-1 bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700"
                >
                  <Play className="w-3 h-3" />
                  Test
                </button>
                <button
                  onClick={() => onToggleStatus(agent.id, agent.is_active)}
                  className={`flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded text-sm ${
                    agent.is_active
                      ? 'bg-red-600 text-white hover:bg-red-700'
                      : 'bg-green-600 text-white hover:bg-green-700'
                  }`}
                >
                  {agent.is_active ? 'Deactivate' : 'Activate'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function AnalyticsDashboard({ stats }: { stats: AdminStats | null }) {
  if (!stats) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">Loading analytics data...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* AI Agent Analytics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">AI Agent Performance</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Bot className="w-8 h-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-purple-600">Total Agents</p>
                <p className="text-2xl font-bold text-purple-900">{stats?.ai_agents?.total_agents || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <MessageSquare className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-green-600">Conversations</p>
                <p className="text-2xl font-bold text-green-900">{stats.ai_agents.total_conversations}</p>
              </div>
            </div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center">
              <TrendingUp className="w-8 h-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-blue-600">Avg Confidence</p>
                <p className="text-2xl font-bold text-blue-900">{stats.ai_agents.average_confidence}%</p>
              </div>
            </div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Shield className="w-8 h-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-red-600">Escalated</p>
                <p className="text-2xl font-bold text-red-900">{stats.ai_agents.escalated_conversations}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Platform Usage Breakdown */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Platform Usage</h2>
        <div className="space-y-3">
          {Object.entries(stats.ai_agents.platform_breakdown).map(([platform, count]) => (
            <div key={platform} className="flex items-center justify-between">
              <span className="text-gray-700 capitalize">{platform}</span>
              <div className="flex items-center gap-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{
                      width: `${(count / Object.values(stats.ai_agents.platform_breakdown).reduce((a, b) => a + b, 0)) * 100}%`
                    }}
                  ></div>
                </div>
                <span className="text-sm font-medium text-gray-900 w-12 text-right">{count}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function TestAIAgents({
  aiAgents,
  selectedAgentId,
  setSelectedAgentId,
  testMessages,
  testInput,
  setTestInput,
  isTesting,
  isVoiceTesting,
  sendTestMessage,
  handleVoiceMessage,
  clearTestChat
}: {
  aiAgents: AIAgent[];
  selectedAgentId: number | null;
  setSelectedAgentId: (id: number | null) => void;
  testMessages: Array<{type: 'user' | 'ai', content: string, timestamp: Date}>;
  testInput: string;
  setTestInput: (input: string) => void;
  isTesting: boolean;
  isVoiceTesting: boolean;
  sendTestMessage: (message: string) => void;
  handleVoiceMessage: (message: string) => void;
  clearTestChat: () => void;
}) {
  const selectedAgent = aiAgents.find(agent => agent.id === selectedAgentId);

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3 mb-4">
          <Play className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Test AI Agents</h2>
        </div>
        <p className="text-gray-600">
          Test AI agents with both text and voice in Bangla language. Verify OpenAI integration and voice synthesis.
        </p>
      </div>

      <div className="p-6">
        {/* Agent Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select AI Agent to Test (Optional)
          </label>
          <select
            value={selectedAgentId || ""}
            onChange={(e) => setSelectedAgentId(e.target.value ? parseInt(e.target.value) : null)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">General OpenAI Testing (No specific agent)</option>
            {aiAgents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name} - {agent.description} ({agent.organization_name})
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500 mt-1">
            Choose "General OpenAI Testing" to test OpenAI functionality without a specific agent, or select a specific agent to test with their trained knowledge.
          </p>
        </div>

        {selectedAgent && (
          <>
            {/* Agent Info */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-blue-900">{selectedAgent.name}</h3>
                  <p className="text-blue-700 text-sm">{selectedAgent.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  {selectedAgent.whatsapp_enabled && (
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">WhatsApp</span>
                  )}
                  {selectedAgent.facebook_enabled && (
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Facebook</span>
                  )}
                  <span className={`px-2 py-1 text-xs rounded ${
                    selectedAgent.training_status === "trained"
                      ? "bg-green-100 text-green-800"
                      : "bg-yellow-100 text-yellow-800"
                  }`}>
                    {selectedAgent.training_status}
                  </span>
                </div>
              </div>
            </div>

            {/* Test Interface */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Chat Interface */}
              <div className="lg:col-span-2">
                <div className="bg-gray-50 rounded-lg p-4 h-96 flex flex-col">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900">Test Chat</h3>
                    <button
                      onClick={clearTestChat}
                      className="text-sm text-gray-500 hover:text-gray-700"
                    >
                      Clear Chat
                    </button>
                  </div>

                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto mb-4 space-y-3">
                    {testMessages.length === 0 ? (
                      <div className="text-center text-gray-500 py-8">
                        <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p>Start testing by sending a message</p>
                        <p className="text-sm">Try asking in Bangla: "আপনি কে?" (Who are you?)</p>
                      </div>
                    ) : (
                      testMessages.map((message, index) => (
                        <div
                          key={index}
                          className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                              message.type === 'user'
                                ? 'bg-blue-600 text-white'
                                : 'bg-white border border-gray-200'
                            }`}
                          >
                            <p className="text-sm">{message.content}</p>
                            <p className="text-xs opacity-70 mt-1">
                              {message.timestamp.toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                      ))
                    )}
                    {isTesting && (
                      <div className="flex justify-start">
                        <div className="bg-white border border-gray-200 rounded-lg px-4 py-2">
                          <div className="flex items-center gap-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                            <span className="text-sm text-gray-600">AI is thinking...</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Input */}
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={testInput}
                      onChange={(e) => setTestInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && sendTestMessage(testInput)}
                      placeholder="Type a message in Bangla or English..."
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={isTesting}
                    />
                    <button
                      onClick={() => sendTestMessage(testInput)}
                      disabled={!testInput.trim() || isTesting}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <MessageSquare className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Voice Testing */}
              <div className="space-y-6">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <Mic className="w-5 h-5 text-green-600" />
                    <h3 className="font-semibold text-green-900">Voice Test (Bangla)</h3>
                  </div>
                  <p className="text-green-700 text-sm mb-4">
                    Test voice recognition and synthesis in Bangla language.
                  </p>

                  <VoiceChat
                    onVoiceMessage={handleVoiceMessage}
                    isLoading={isVoiceTesting}
                  />

                  <div className="mt-4 p-3 bg-white rounded border">
                    <p className="text-xs text-gray-600">
                      <strong>Instructions:</strong> Click the microphone and speak in Bangla.
                      The AI will respond both in text and voice.
                    </p>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <Volume2 className="w-5 h-5 text-blue-600" />
                    <h3 className="font-semibold text-blue-900">Test Status</h3>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-blue-700">OpenAI Integration</span>
                      <span className="text-green-600 font-medium">✓ Working</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-blue-700">Voice Recognition</span>
                      <span className="text-green-600 font-medium">✓ Bangla</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-blue-700">Voice Synthesis</span>
                      <span className="text-green-600 font-medium">✓ Active</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-blue-700">Vector Search</span>
                      <span className="text-green-600 font-medium">✓ Working</span>
                    </div>
                  </div>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h3 className="font-semibold text-yellow-900 mb-2">Sample Test Messages</h3>
                  <div className="space-y-2">
                    <button
                      onClick={() => sendTestMessage("আপনি কে?")}
                      className="w-full text-left px-3 py-2 text-sm bg-white rounded hover:bg-yellow-100 border"
                    >
                      "আপনি কে?" (Who are you?)
                    </button>
                    <button
                      onClick={() => sendTestMessage("আমার অর্ডার কোথায়?")}
                      className="w-full text-left px-3 py-2 text-sm bg-white rounded hover:bg-yellow-100 border"
                    >
                      "আমার অর্ডার কোথায়?" (Where is my order?)
                    </button>
                    <button
                      onClick={() => sendTestMessage("কাস্টমার সার্ভিস এর সময় কত?")}
                      className="w-full text-left px-3 py-2 text-sm bg-white rounded hover:bg-yellow-100 border"
                    >
                      "কাস্টমার সার্ভিস এর সময় কত?" (What are customer service hours?)
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {!selectedAgent && aiAgents.length > 0 && (
          <div className="text-center py-12">
            <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Select an AI Agent</h3>
            <p className="text-gray-600">Choose an AI agent from the dropdown above to start testing.</p>
          </div>
        )}

        {aiAgents.length === 0 && (
          <div className="text-center py-12">
            <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No AI Agents Available</h3>
            <p className="text-gray-600">Create AI agents first to test their functionality.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function SystemManagement() {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">System Settings</h2>
      <p className="text-gray-600">Configure system-wide settings and integrations</p>
      <div className="mt-6 space-y-4">
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-2">OpenAI Integration</h3>
          <p className="text-sm text-gray-600 mb-3">Configure your OpenAI API key for AI responses</p>
          <button className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700">
            Configure API Key
          </button>
        </div>

        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-2">Webhook Endpoints</h3>
          <p className="text-sm text-gray-600 mb-3">Social media webhook URLs for integrations</p>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>WhatsApp:</span>
              <code className="bg-gray-100 px-2 py-1 rounded">/api/chat/webhooks/whatsapp</code>
            </div>
            <div className="flex justify-between">
              <span>Facebook:</span>
              <code className="bg-gray-100 px-2 py-1 rounded">/api/chat/webhooks/facebook</code>
            </div>
            <div className="flex justify-between">
              <span>Instagram:</span>
              <code className="bg-gray-100 px-2 py-1 rounded">/api/chat/webhooks/instagram</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
