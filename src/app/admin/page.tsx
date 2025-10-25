"use client";

import {
  Users,
  Building,
  Bot,
  MessageSquare,
  BarChart3,
  Activity,
  CheckCircle,
  AlertTriangle,
  Plus,
  LogOut,
  Shield,
  TrendingUp
} from "lucide-react";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface Client {
  id: number;
  name: string;
  email: string;
  plan: string;
  status: 'active' | 'inactive' | 'suspended';
  created_at: string;
  ai_agents_count: number;
  total_messages: number;
  subscription_end?: string;
}

interface AIAgent {
  id: number;
  name: string;
  client_id: number;
  client_name: string;
  status: 'active' | 'inactive';
  whatsapp_enabled: boolean;
  facebook_enabled: boolean;
  instagram_enabled: boolean;
  total_conversations: number;
}

interface Payment {
  id: number;
  client_id: number;
  client_name: string;
  amount: number;
  status: 'paid' | 'pending' | 'failed';
  type: 'subscription' | 'one-time';
  created_at: string;
}

function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [clients, setClients] = useState<Client[]>([]);
  const [aiAgents, setAiAgents] = useState<AIAgent[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [testMessage, setTestMessage] = useState("");
  const [selectedAgent, setSelectedAgent] = useState<number | null>(null);
  const [testResponse, setTestResponse] = useState<string>("");
  const [isTesting, setIsTesting] = useState(false);
  const router = useRouter();

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        router.push("/login");
        return;
      }

      // Load clients
      const clientsResponse = await fetch("/api/admin/clients", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (clientsResponse.ok) {
        const clientsData = await clientsResponse.json();
        setClients(clientsData);
      }

      // Load AI agents
      const agentsResponse = await fetch("/api/admin/ai-agents", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (agentsResponse.ok) {
        const agentsData = await agentsResponse.json();
        setAiAgents(agentsData);
      }

      // Load payments
      const paymentsResponse = await fetch("/api/admin/payments", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (paymentsResponse.ok) {
        const paymentsData = await paymentsResponse.json();
        setPayments(paymentsData);
      }
    } catch (error) {
      console.error("Failed to load admin data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleClientStatusChange = async (clientId: number, newStatus: 'active' | 'inactive' | 'suspended') => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/api/admin/clients/${clientId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ status: newStatus })
      });

      if (response.ok) {
        // Update local state
        setClients(prev => prev.map(client =>
          client.id === clientId ? { ...client, status: newStatus } : client
        ));

        // Refresh data to get updated AI agent statuses
        await loadAdminData();
      }
    } catch (error) {
      console.error("Failed to update client status:", error);
    }
  };

  const handleAgentStatusChange = async (agentId: number, newStatus: 'active' | 'inactive') => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/api/admin/ai-agents/${agentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ is_active: newStatus === 'active' })
      });

      if (response.ok) {
        // Update local state
        setAiAgents(prev => prev.map(agent =>
          agent.id === agentId ? { ...agent, status: newStatus } : agent
        ));
      }
    } catch (error) {
      console.error("Failed to update agent status:", error);
    }
  };

  const testAI = async () => {
    if (!testMessage.trim()) return;

    setIsTesting(true);
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("/api/admin/test-ai", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          message: testMessage,
          ai_agent_id: selectedAgent
        })
      });

      if (response.ok) {
        const data = await response.json();
        setTestResponse(`AI Response: ${data.response}\nConfidence: ${(data.confidence * 100).toFixed(1)}%`);
      } else {
        setTestResponse("Error: Failed to test AI agent");
      }
    } catch (error) {
      console.error("Failed to test AI:", error);
      setTestResponse("Error: Network connection failed");
    } finally {
      setIsTesting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-xl shadow-lg border-b border-white/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-gradient-to-r from-red-500 to-orange-500 rounded-xl flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Platform Admin</h1>
                <p className="text-xs text-gray-500">Manage all clients & AI agents</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="hidden sm:flex items-center gap-2 bg-green-50 px-3 py-1 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-green-700 font-medium">All Systems Operational</span>
              </div>
              <span className="text-sm text-gray-600 bg-red-50 px-3 py-1 rounded-lg">
                Admin Access
              </span>
              <button
                onClick={() => router.push("/")}
                className="bg-white/80 backdrop-blur-sm text-gray-700 px-4 py-2 rounded-lg hover:bg-white/90 transition-colors border border-gray-200"
              >
                <LogOut className="w-4 h-4 inline mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-white/20">
            <div className="flex items-center justify-between mb-4">
              <Users className="w-8 h-8 text-blue-500" />
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">156</div>
            <div className="text-sm text-gray-600">Total Users</div>
          </div>

          <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-white/20">
            <div className="flex items-center justify-between mb-4">
              <Building className="w-8 h-8 text-green-500" />
              <Activity className="w-5 h-5 text-green-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">23</div>
            <div className="text-sm text-gray-600">Organizations</div>
          </div>

          <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-white/20">
            <div className="flex items-center justify-between mb-4">
              <Bot className="w-8 h-8 text-purple-500" />
              <CheckCircle className="w-5 h-5 text-green-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">89</div>
            <div className="text-sm text-gray-600">AI Agents</div>
          </div>

          <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-white/20">
            <div className="flex items-center justify-between mb-4">
              <MessageSquare className="w-8 h-8 text-orange-500" />
              <Activity className="w-5 h-5 text-orange-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">45.2K</div>
            <div className="text-sm text-gray-600">Total Messages</div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-white/20">
              <nav className="space-y-2">
                <button
                  onClick={() => setActiveTab('dashboard')}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                    activeTab === 'dashboard'
                      ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                      : 'text-gray-700 hover:bg-gray-50 rounded-xl'
                  }`}
                >
                  <BarChart3 className="w-5 h-5" />
                  Dashboard
                </button>
                <button
                  onClick={() => setActiveTab('clients')}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                    activeTab === 'clients'
                      ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                      : 'text-gray-700 hover:bg-gray-50 rounded-xl'
                  }`}
                >
                  <Building className="w-5 h-5" />
                  Clients
                </button>
                <button
                  onClick={() => setActiveTab('agents')}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                    activeTab === 'agents'
                      ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                      : 'text-gray-700 hover:bg-gray-50 rounded-xl'
                  }`}
                >
                  <Bot className="w-5 h-5" />
                  AI Agents
                </button>
                <button
                  onClick={() => setActiveTab('payments')}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                    activeTab === 'payments'
                      ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                      : 'text-gray-700 hover:bg-gray-50 rounded-xl'
                  }`}
                >
                  <TrendingUp className="w-5 h-5" />
                  Payments
                </button>
              <button
                onClick={() => setActiveTab('testing')}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                  activeTab === 'testing'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-gray-50 rounded-xl'
                }`}
              >
                <MessageSquare className="w-5 h-5" />
                Test AI
              </button>
              <button
                onClick={() => setActiveTab('profile')}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                  activeTab === 'profile'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-gray-50 rounded-xl'
                }`}
              >
                <Shield className="w-5 h-5" />
                Profile
              </button>
              <button
                onClick={() => setActiveTab('settings')}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                  activeTab === 'settings'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                    : 'text-gray-700 hover:bg-gray-50 rounded-xl'
                }`}
              >
                <Settings className="w-5 h-5" />
                Settings
              </button>
            </nav>
            </div>
          </div>

          {/* Content Area */}
          <div className="lg:col-span-3">
            {activeTab === 'dashboard' && (
              <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-white/20">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Platform Overview</h2>

                {/* Recent Activity */}
                <div className="mb-8">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
                  <div className="space-y-4">
                    <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                      <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                        <Plus className="w-5 h-5 text-green-600" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">New organization registered</p>
                        <p className="text-sm text-gray-600">TechCorp Solutions joined the platform</p>
                      </div>
                      <span className="text-sm text-gray-500">2 hours ago</span>
                    </div>

                    <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <Bot className="w-5 h-5 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">AI Agent created</p>
                        <p className="text-sm text-gray-600">Customer Support Agent trained for E-commerce</p>
                      </div>
                      <span className="text-sm text-gray-500">4 hours ago</span>
                    </div>

                    <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                      <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                        <MessageSquare className="w-5 h-5 text-purple-600" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">High message volume</p>
                        <p className="text-sm text-gray-600">FashionStore processed 500+ messages today</p>
                      </div>
                      <span className="text-sm text-gray-500">6 hours ago</span>
                    </div>
                  </div>
                </div>

                {/* System Health */}
                <div className="mb-8">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-green-900">API Services</span>
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      </div>
                      <p className="text-sm text-green-700">All services operational</p>
                    </div>

                    <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-green-900">Database</span>
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      </div>
                      <p className="text-sm text-green-700">99.9% uptime this month</p>
                    </div>

                    <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-yellow-900">Background Jobs</span>
                        <AlertTriangle className="w-5 h-5 text-yellow-600" />
                      </div>
                      <p className="text-sm text-yellow-700">2 jobs queued</p>
                    </div>
                  </div>
                </div>

                {/* Quick Actions */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <button
                      onClick={() => setActiveTab('clients')}
                      className="flex items-center gap-3 p-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all duration-300"
                    >
                      <Users className="w-5 h-5" />
                      Manage Clients
                    </button>
                    <button
                      onClick={() => setActiveTab('agents')}
                      className="flex items-center gap-3 p-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:from-green-600 hover:to-emerald-600 transition-all duration-300"
                    >
                      <Bot className="w-5 h-5" />
                      Manage AI Agents
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'clients' && (
              <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-white/20">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">Client Management</h2>
                  <button className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-colors">
                    Add New Client
                  </button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Client</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Plan</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Status</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">AI Agents</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Messages</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {clients.map((client) => (
                        <tr key={client.id} className="border-b border-gray-100">
                          <td className="py-4 px-4">
                            <div>
                              <div className="font-medium text-gray-900">{client.name}</div>
                              <div className="text-sm text-gray-600">{client.email}</div>
                            </div>
                          </td>
                          <td className="py-4 px-4">
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                              {client.plan}
                            </span>
                          </td>
                          <td className="py-4 px-4">
                            <select
                              value={client.status}
                              onChange={(e) => handleClientStatusChange(client.id, e.target.value as 'active' | 'inactive' | 'suspended')}
                              className={`px-2 py-1 rounded-full text-xs font-medium ${
                                client.status === 'active' ? 'bg-green-100 text-green-800' :
                                client.status === 'inactive' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-red-100 text-red-800'
                              }`}
                            >
                              <option value="active">Active</option>
                              <option value="inactive">Inactive</option>
                              <option value="suspended">Suspended</option>
                            </select>
                          </td>
                          <td className="py-4 px-4">{client.ai_agents_count}</td>
                          <td className="py-4 px-4">{client.total_messages.toLocaleString()}</td>
                          <td className="py-4 px-4">
                            <button className="text-blue-600 hover:text-blue-800 text-sm mr-3">
                              Edit
                            </button>
                            <button className="text-red-600 hover:text-red-800 text-sm">
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'agents' && (
              <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-white/20">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">AI Agent Management</h2>
                  <button className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-4 py-2 rounded-lg hover:from-green-600 hover:to-emerald-600 transition-colors">
                    Create New Agent
                  </button>
                </div>

                <div className="space-y-6">
                  {aiAgents.map((agent) => (
                    <div key={agent.id} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                          <p className="text-sm text-gray-600">Client: {agent.client_name}</p>
                        </div>
                        <div className="flex items-center gap-3">
                          <select
                            value={agent.status}
                            onChange={(e) => handleAgentStatusChange(agent.id, e.target.value as 'active' | 'inactive')}
                            className={`px-3 py-1 rounded-full text-sm font-medium ${
                              agent.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                          </select>
                          <button className="text-blue-600 hover:text-blue-800 text-sm">
                            Configure
                          </button>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-gray-900">{agent.total_conversations}</div>
                          <div className="text-sm text-gray-600">Conversations</div>
                        </div>
                        <div className="flex justify-center">
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                            agent.whatsapp_enabled ? 'bg-green-500' : 'bg-gray-300'
                          }`}>
                            <span className="text-xs text-white">📱</span>
                          </div>
                          <span className="ml-2 text-sm text-gray-600">WhatsApp</span>
                        </div>
                        <div className="flex justify-center">
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                            agent.facebook_enabled ? 'bg-blue-500' : 'bg-gray-300'
                          }`}>
                            <span className="text-xs text-white">📘</span>
                          </div>
                          <span className="ml-2 text-sm text-gray-600">Facebook</span>
                        </div>
                        <div className="flex justify-center">
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                            agent.instagram_enabled ? 'bg-pink-500' : 'bg-gray-300'
                          }`}>
                            <span className="text-xs text-white">📷</span>
                          </div>
                          <span className="ml-2 text-sm text-gray-600">Instagram</span>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <button className="text-sm bg-blue-50 text-blue-700 px-3 py-1 rounded hover:bg-blue-100">
                          View Conversations
                        </button>
                        <button className="text-sm bg-green-50 text-green-700 px-3 py-1 rounded hover:bg-green-100">
                          Edit Settings
                        </button>
                        <button className="text-sm bg-red-50 text-red-700 px-3 py-1 rounded hover:bg-red-100">
                          Delete Agent
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'payments' && (
              <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-white/20">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">Payment Management</h2>
                  <button className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-colors">
                    Process Payment
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl">
                    <div className="text-2xl font-bold text-green-600 mb-2">$12,450</div>
                    <div className="text-sm text-green-700">Monthly Revenue</div>
                  </div>
                  <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-6 rounded-xl">
                    <div className="text-2xl font-bold text-blue-600 mb-2">23</div>
                    <div className="text-sm text-blue-700">Active Subscriptions</div>
                  </div>
                  <div className="bg-gradient-to-r from-orange-50 to-red-50 p-6 rounded-xl">
                    <div className="text-2xl font-bold text-orange-600 mb-2">3</div>
                    <div className="text-sm text-orange-700">Failed Payments</div>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Client</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Amount</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Type</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Status</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Date</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {payments.map((payment) => (
                        <tr key={payment.id} className="border-b border-gray-100">
                          <td className="py-4 px-4">
                            <div className="font-medium text-gray-900">{payment.client_name}</div>
                          </td>
                          <td className="py-4 px-4 font-semibold">${payment.amount}</td>
                          <td className="py-4 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              payment.type === 'subscription' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                            }`}>
                              {payment.type}
                            </span>
                          </td>
                          <td className="py-4 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              payment.status === 'paid' ? 'bg-green-100 text-green-800' :
                              payment.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {payment.status}
                            </span>
                          </td>
                          <td className="py-4 px-4 text-sm text-gray-600">
                            {new Date(payment.created_at).toLocaleDateString()}
                          </td>
                          <td className="py-4 px-4">
                            <button className="text-blue-600 hover:text-blue-800 text-sm mr-3">
                              View
                            </button>
                            {payment.status === 'failed' && (
                              <button className="text-green-600 hover:text-green-800 text-sm">
                                Retry
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'testing' && (
              <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-white/20">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">AI Agent Testing</h2>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Chat Test Interface */}
                  <div className="border border-gray-200 rounded-lg p-6">
                    <h3 className="font-semibold text-gray-900 mb-4">Test Chat Agent</h3>

                    <div className="mb-4">
                      <select
                        value={selectedAgent || ""}
                        onChange={(e) => setSelectedAgent(e.target.value ? parseInt(e.target.value) : null)}
                        className="w-full p-2 border border-gray-300 rounded-lg"
                      >
                        <option value="">Select AI Agent (or leave empty for default)</option>
                        {aiAgents.map((agent) => (
                          <option key={agent.id} value={agent.id}>
                            {agent.name} ({agent.client_name})
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4 mb-4 h-64 overflow-y-auto font-mono text-sm">
                      {testResponse ? (
                        <div className="whitespace-pre-wrap text-gray-800">{testResponse}</div>
                      ) : (
                        <div className="text-center text-gray-500">
                          Test responses will appear here
                        </div>
                      )}
                    </div>

                    <div className="flex gap-2 mb-4">
                      <input
                        type="text"
                        value={testMessage}
                        onChange={(e) => setTestMessage(e.target.value)}
                        placeholder="Type your test message..."
                        className="flex-1 p-2 border border-gray-300 rounded-lg"
                        onKeyPress={(e) => e.key === 'Enter' && testAI()}
                      />
                      <button
                        onClick={testAI}
                        disabled={isTesting || !testMessage.trim()}
                        className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
                      >
                        {isTesting ? 'Testing...' : 'Test'}
                      </button>
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => setTestResponse("")}
                        className="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
                      >
                        Clear
                      </button>
                      <button
                        onClick={() => setTestMessage("")}
                        className="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
                      >
                        Clear Input
                      </button>
                    </div>
                  </div>

                  {/* Voice Test Interface */}
                  <div className="border border-gray-200 rounded-lg p-6">
                    <h3 className="font-semibold text-gray-900 mb-4">Voice Call Simulation</h3>

                    <div className="mb-4">
                      <select className="w-full p-2 border border-gray-300 rounded-lg">
                        <option>Select AI Agent for IVR</option>
                        {aiAgents.map((agent) => (
                          <option key={agent.id} value={agent.id}>
                            {agent.name} ({agent.client_name})
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4 mb-4 h-48 overflow-y-auto">
                      <div className="text-center text-gray-500 text-sm">
                        IVR simulation will show call flow and responses here
                      </div>
                    </div>

                    <div className="mb-4">
                      <p className="text-sm text-gray-600 mb-2">Quick Test Scenarios:</p>
                      <div className="grid grid-cols-2 gap-2">
                        <button className="bg-blue-100 text-blue-800 px-3 py-2 rounded text-sm hover:bg-blue-200">
                          Order Status
                        </button>
                        <button className="bg-green-100 text-green-800 px-3 py-2 rounded text-sm hover:bg-green-200">
                          Product Info
                        </button>
                        <button className="bg-purple-100 text-purple-800 px-3 py-2 rounded text-sm hover:bg-purple-200">
                          Support Request
                        </button>
                        <button className="bg-orange-100 text-orange-800 px-3 py-2 rounded text-sm hover:bg-orange-200">
                          Speak to Human
                        </button>
                      </div>
                    </div>

                    <div className="text-center">
                      <button className="w-full bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600">
                        Start IVR Test
                      </button>
                    </div>
                  </div>
                </div>

                {/* Test Instructions */}
                <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h3 className="font-semibold text-blue-900 mb-3">Testing Instructions</h3>
                  <ul className="text-blue-800 text-sm space-y-2">
                    <li>• Select an AI agent from the dropdown or leave empty to test the default agent</li>
                    <li>• Enter a test message and click "Test" to see how the AI responds</li>
                    <li>• Voice testing simulates IVR calls with common customer scenarios</li>
                    <li>• All tests run in sandbox mode and don't affect live customer conversations</li>
                  </ul>
                </div>
              </div>
            )}

            {activeTab === 'profile' && (
              <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-white/20">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Admin Profile & Account</h2>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Personal Information */}
                  <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-6 rounded-xl">
                    <h3 className="font-bold text-gray-900 mb-6 flex items-center">
                      <Shield className="w-5 h-5 mr-2" />
                      Personal Information
                    </h3>

                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Full Name
                        </label>
                        <div className="bg-white px-3 py-2 rounded-lg border border-gray-200">
                          Platform Administrator
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Username
                        </label>
                        <div className="bg-white px-3 py-2 rounded-lg border border-gray-200">
                          admin
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Email Address
                        </label>
                        <div className="bg-white px-3 py-2 rounded-lg border border-gray-200">
                          admin@bdchatpro.com
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Account Type
                        </label>
                        <div className="bg-white px-3 py-2 rounded-lg border border-gray-200 capitalize">
                          Platform Administrator
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Access Level
                        </label>
                        <div className="bg-green-100 text-green-800 px-3 py-2 rounded-lg border border-green-200 font-medium">
                          Super User
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* System Statistics */}
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl">
                    <h3 className="font-bold text-gray-900 mb-6 flex items-center">
                      <Activity className="w-5 h-5 mr-2" />
                      System Overview
                    </h3>

                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Total Organizations
                        </label>
                        <div className="bg-white px-3 py-2 rounded-lg border border-gray-200">
                          4 Active Organizations
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Total AI Agents
                        </label>
                        <div className="bg-white px-3 py-2 rounded-lg border border-gray-200">
                          3 Deployed Agents
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          System Status
                        </label>
                        <div className="bg-green-100 text-green-800 px-3 py-2 rounded-lg border border-green-200 font-medium">
                          All Systems Operational
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Platform Uptime
                        </label>
                        <div className="bg-white px-3 py-2 rounded-lg border border-gray-200">
                          99.9% (30 days)
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Admin Permissions */}
                <div className="mt-8 bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-xl">
                  <h3 className="font-bold text-gray-900 mb-6 flex items-center">
                    <Star className="w-5 h-5 mr-2" />
                    Administrator Permissions
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <div className="flex items-center mb-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                        <span className="text-sm font-medium text-gray-900">Client Management</span>
                      </div>
                      <div className="text-xs text-gray-600">Create, modify, and manage client accounts</div>
                    </div>

                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <div className="flex items-center mb-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                        <span className="text-sm font-medium text-gray-900">AI Agent Control</span>
                      </div>
                      <div className="text-xs text-gray-600">Deploy and manage AI agents across platforms</div>
                    </div>

                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <div className="flex items-center mb-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                        <span className="text-sm font-medium text-gray-900">System Monitoring</span>
                      </div>
                      <div className="text-xs text-gray-600">Monitor platform health and performance</div>
                    </div>

                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <div className="flex items-center mb-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                        <span className="text-sm font-medium text-gray-900">Billing Management</span>
                      </div>
                      <div className="text-xs text-gray-600">Handle subscriptions and payment processing</div>
                    </div>

                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <div className="flex items-center mb-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                        <span className="text-sm font-medium text-gray-900">Security Oversight</span>
                      </div>
                      <div className="text-xs text-gray-600">Manage platform security and access controls</div>
                    </div>

                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <div className="flex items-center mb-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                        <span className="text-sm font-medium text-gray-900">Support Access</span>
                      </div>
                      <div className="text-xs text-gray-600">Full access to support and troubleshooting tools</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-white/20">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Admin Settings</h2>

                <div className="space-y-8">
                  {/* Platform Settings */}
                  <div className="bg-white rounded-xl shadow-lg p-6">
                    <h3 className="font-bold text-gray-900 mb-6 flex items-center">
                      <Settings className="w-5 h-5 mr-2" />
                      Platform Configuration
                    </h3>

                    <div className="space-y-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Default AI Model
                        </label>
                        <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                          <option>GPT-4 Turbo</option>
                          <option>GPT-4</option>
                          <option>GPT-3.5 Turbo</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Maximum Monthly Messages per Client
                        </label>
                        <input
                          type="number"
                          defaultValue="10000"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">Maintenance Mode</div>
                          <div className="text-sm text-gray-600">Temporarily disable platform access for maintenance</div>
                        </div>
                        <input type="checkbox" className="w-4 h-4 text-blue-600" />
                      </div>
                    </div>
                  </div>

                  {/* Security Settings */}
                  <div className="bg-white rounded-xl shadow-lg p-6">
                    <h3 className="font-bold text-gray-900 mb-6 flex items-center">
                      <Shield className="w-5 h-5 mr-2" />
                      Security Settings
                    </h3>

                    <div className="space-y-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Change Admin Password
                        </label>
                        <div className="space-y-3">
                          <input
                            type="password"
                            placeholder="Current password"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                          <input
                            type="password"
                            placeholder="New password"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                          <input
                            type="password"
                            placeholder="Confirm new password"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                          <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                            Update Password
                          </button>
                        </div>
                      </div>

                      <div className="border-t border-gray-200 pt-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium text-gray-900">Two-Factor Authentication</div>
                            <div className="text-sm text-gray-600">Enable 2FA for admin account</div>
                          </div>
                          <button className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors">
                            Enable 2FA
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* System Maintenance */}
                  <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
                    <h3 className="font-bold text-yellow-900 mb-6 flex items-center">
                      <AlertTriangle className="w-5 h-5 mr-2" />
                      System Maintenance
                    </h3>

                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-yellow-900">Database Backup</div>
                          <div className="text-sm text-yellow-700">Create a backup of all platform data</div>
                        </div>
                        <button className="bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition-colors">
                          Backup Now
                        </button>
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-yellow-900">Clear System Logs</div>
                          <div className="text-sm text-yellow-700">Remove old system logs to free up space</div>
                        </div>
                        <button className="bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition-colors">
                          Clear Logs
                        </button>
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-yellow-900">Restart Services</div>
                          <div className="text-sm text-yellow-700">Restart all platform services</div>
                        </div>
                        <button className="bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition-colors">
                          Restart
                        </button>
                      </div>
                    </div>
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

export default AdminDashboard;