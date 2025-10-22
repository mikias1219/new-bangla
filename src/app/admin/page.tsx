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
  Volume2,
  Plus,
  Trash2,
  CheckCircle,
  Languages,
  Send
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
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
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
        endpoint = `/api/chat/agents/${selectedAgentId}/chat`;
      } else {
        // General OpenAI testing without specific agent
        endpoint = `/api/admin/test-openai?message=${encodeURIComponent(message.trim())}`;
        requestBody = {};
      }

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        ...(Object.keys(requestBody).length > 0 && { body: JSON.stringify(requestBody) }),
      });

      if (response.ok) {
        const data = await response.json();
        const aiResponse = selectedAgentId ? data.response : data.response;
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
          ...(newAgentData.description.trim() && { description: newAgentData.description.trim() }),
          ...(newAgentData.systemPrompt.trim() && { system_prompt: newAgentData.systemPrompt.trim() })
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
            <div className="flex items-center gap-4">
              {/* Mobile sidebar toggle */}
              <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="lg:hidden p-2 text-gray-600 hover:text-gray-900"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  {isSidebarOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
              <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Admin Dashboard</h1>
            </div>
            <div className="flex items-center gap-2 sm:gap-4">
              <span className="hidden sm:inline text-gray-700">Administrator</span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 text-sm sm:text-base"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className={`lg:col-span-1 ${isSidebarOpen ? 'block' : 'hidden lg:block'}`}>
            <div className="bg-white rounded-lg shadow p-4 sm:p-6">
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
          <div className="lg:col-span-3" onClick={() => isSidebarOpen && setIsSidebarOpen(false)}>
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
      {/* Header with Actions */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Agent Selection - Compact */}
            <select
              value={selectedAgentId || ""}
              onChange={(e) => setSelectedAgentId(e.target.value ? parseInt(e.target.value) : null)}
              className="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
            >
              <option value="">General AI Test</option>
              {aiAgents.map((agent) => (
                <option key={agent.id} value={agent.id}>
                  {agent.name}
                </option>
              ))}
            </select>
            {/* Agent Status */}
            {selectedAgent && (
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-gray-900">{selectedAgent.name}</span>
                <span className={`px-2 py-0.5 text-xs rounded-full ${
                  selectedAgent.training_status === "trained"
                    ? "bg-green-100 text-green-800"
                    : "bg-yellow-100 text-yellow-800"
                }`}>
                  {selectedAgent.training_status}
                </span>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={clearTestChat}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
              title="Clear chat"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Chat Area */}
        <div className="flex-1 p-4">
          <div className="bg-gray-50 rounded-lg h-[500px] flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {testMessages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <Bot className="w-16 h-16 text-gray-300 mb-4" />
                  <p className="text-gray-500 text-sm">Start a conversation</p>
                  <p className="text-gray-400 text-xs mt-1">Type or use voice in any language</p>
                </div>
              ) : (
                testMessages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[320px] px-4 py-3 rounded-2xl shadow-sm ${
                        message.type === 'user'
                          ? 'bg-blue-600 text-white rounded-br-sm'
                          : 'bg-white text-gray-900 rounded-bl-sm border border-gray-100'
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>
                      <p className={`text-xs mt-1 ${message.type === 'user' ? 'text-blue-100' : 'text-gray-400'}`}>
                        {message.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </p>
                    </div>
                  </div>
                ))
              )}
              {isTesting && (
                <div className="flex justify-start">
                  <div className="bg-white border border-gray-100 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                    <div className="flex items-center gap-2">
                      <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600"></div>
                      <span className="text-sm text-gray-600">AI is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-gray-200 bg-white rounded-b-lg">
              <div className="flex items-center gap-3">
                {/* Voice Button */}
                <VoiceChat
                  onVoiceMessage={handleVoiceMessage}
                  isLoading={isVoiceTesting}
                />

                {/* Text Input */}
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={testInput}
                    onChange={(e) => setTestInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendTestMessage(testInput)}
                    placeholder="Type your message... (supports English, Bangla, etc.)"
                    className="w-full px-4 py-3 pr-12 bg-white border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 shadow-sm"
                    disabled={isTesting}
                  />
                  <button
                    onClick={() => sendTestMessage(testInput)}
                    disabled={!testInput.trim() || isTesting}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Status Panel */}
        <div className="w-64 border-l border-gray-200 p-4 bg-gray-50">
          <div className="space-y-4">
            {/* Status Indicators */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-gray-700">OpenAI</span>
                </div>
                <CheckCircle className="w-4 h-4 text-green-600" />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-sm text-gray-700">Voice</span>
                </div>
                <Mic className="w-4 h-4 text-blue-600" />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span className="text-sm text-gray-700">Languages</span>
                </div>
                <Languages className="w-4 h-4 text-purple-600" />
              </div>
            </div>

            {/* Language Info */}
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Multi-Language Support</h4>
              <div className="space-y-1 text-xs text-gray-600">
                <div>• English ↔ English</div>
                <div>• বাংলা ↔ বাংলা</div>
                <div>• Voice in all languages</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
