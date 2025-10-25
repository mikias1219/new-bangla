"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Bot,
  Upload,
  MessageSquare,
  Users,
  FileText,
  TrendingUp,
  Settings,
  Plus,
  Play,
  Pause,
  Trash2,
  Eye,
  BarChart3,
  Smartphone,
  Facebook,
  Instagram,
  Phone,
  Zap,
  Shield,
  Activity,
  Star,
  Clock,
  Target,
  CheckCircle,
  AlertTriangle,
  Link,
  Database,
  Globe,
  Building
} from "lucide-react";

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
  const [activeTab, setActiveTab] = useState("overview");
  const [agents, setAgents] = useState<AIAgent[]>([]);
  const [documents, setDocuments] = useState<TrainingDocument[]>([]);
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [chatMessages, setChatMessages] = useState<{role: 'user' | 'assistant', content: string, timestamp: Date}[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [selectedAgentId, setSelectedAgentId] = useState<number | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const router = useRouter();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        router.push("/login");
        return;
      }

      // Load organization data
      const orgResponse = await fetch("/api/organizations/me", {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (orgResponse.ok) {
        const orgData = await orgResponse.json();
        setOrganization(orgData);
      }

      // Load user data
      const userResponse = await fetch("/api/users/me", {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (userResponse.ok) {
        const userData = await userResponse.json();
        setUser(userData);
      }

      // Load AI agents
      const agentsResponse = await fetch("/api/organizations/agents", {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (agentsResponse.ok) {
        const agentsData = await agentsResponse.json();
        setAgents(agentsData);
      }

      // Load documents
      const docsResponse = await fetch("/api/organizations/documents", {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (docsResponse.ok) {
        const docsData = await docsResponse.json();
        setDocuments(docsData);
      }
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/");
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = { role: 'user' as const, content: chatInput, timestamp: new Date() };
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput("");
    setIsTyping(true);

    try {
      const token = localStorage.getItem("token");
      const response = await fetch("/api/admin/test-ai", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          message: chatInput,
          ai_agent_id: selectedAgentId
        })
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage = {
          role: 'assistant' as const,
          content: data.response,
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, aiMessage]);
      } else {
        const errorMessage = {
          role: 'assistant' as const,
          content: "Sorry, I'm having trouble connecting to the AI service right now. Please try again later.",
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage = {
        role: 'assistant' as const,
        content: "Network error. Please check your connection and try again.",
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const clearChat = () => {
    setChatMessages([]);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
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
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">{organization?.name || "Client Dashboard"}</h1>
                <p className="text-xs text-gray-500">AI Customer Service Management</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="hidden sm:flex items-center gap-2 bg-green-50 px-3 py-1 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-green-700 font-medium">All Systems Operational</span>
              </div>
              <span className="text-sm text-gray-600 bg-white/80 px-3 py-1 rounded-lg">
                Plan: <span className="font-semibold capitalize text-purple-600">{organization?.plan}</span>
              </span>
              <button
                onClick={() => router.push("/")}
                className="bg-white/80 backdrop-blur-sm text-gray-700 px-4 py-2 rounded-lg hover:bg-white/90 transition-colors border border-gray-200"
              >
                ← Back to Home
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 rounded-3xl p-8 text-white mb-8 shadow-2xl">
          <div className="flex flex-col lg:flex-row items-center justify-between">
            <div className="mb-6 lg:mb-0">
              <h1 className="text-3xl lg:text-4xl font-bold mb-2">
                Welcome back, {user?.full_name || user?.username || 'Client'}! 👋
              </h1>
              <p className="text-blue-100 text-lg">
                Your AI agents are handling customer conversations across all platforms
              </p>
            </div>
            <div className="flex gap-4">
              <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4 text-center">
                <div className="text-2xl font-bold">{agents.length}</div>
                <div className="text-sm text-blue-100">AI Agents</div>
              </div>
              <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4 text-center">
                <div className="text-2xl font-bold">
                  {organization ? organization.current_monthly_chats : 0}
                </div>
                <div className="text-sm text-blue-100">This Month</div>
              </div>
              <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4 text-center">
                <div className="text-2xl font-bold">98%</div>
                <div className="text-sm text-blue-100">Satisfaction</div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100 group">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <Plus className="w-6 h-6 text-white" />
              </div>
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <h3 className="font-bold text-gray-900 mb-1">Create AI Agent</h3>
            <p className="text-sm text-gray-600 mb-3">Train a new AI agent for your business</p>
            <button
              onClick={() => setActiveTab("agents")}
              className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white py-2 rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all duration-300"
            >
              Get Started
            </button>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100 group">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <Upload className="w-6 h-6 text-white" />
              </div>
              <Activity className="w-5 h-5 text-green-500" />
            </div>
            <h3 className="font-bold text-gray-900 mb-1">Upload Training Data</h3>
            <p className="text-sm text-gray-600 mb-3">Add documents to improve AI responses</p>
            <button
              onClick={() => setActiveTab("training")}
              className="w-full bg-gradient-to-r from-green-500 to-emerald-500 text-white py-2 rounded-lg hover:from-green-600 hover:to-emerald-600 transition-all duration-300"
            >
              Upload Files
            </button>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100 group">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <Globe className="w-6 h-6 text-white" />
              </div>
              <Zap className="w-5 h-5 text-purple-500" />
            </div>
            <h3 className="font-bold text-gray-900 mb-1">Connect Platforms</h3>
            <p className="text-sm text-gray-600 mb-3">Link WhatsApp, Facebook, Instagram</p>
            <button
              onClick={() => setActiveTab("integrations")}
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-2 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-300"
            >
              Setup Integration
            </button>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100 group">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <Target className="w-5 h-5 text-orange-500" />
            </div>
            <h3 className="font-bold text-gray-900 mb-1">View Analytics</h3>
            <p className="text-sm text-gray-600 mb-3">Monitor performance and insights</p>
            <button
              onClick={() => setActiveTab("analytics")}
              className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white py-2 rounded-lg hover:from-orange-600 hover:to-red-600 transition-all duration-300"
            >
              View Reports
            </button>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Navigation Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-white/20 sticky top-24">
              <nav className="space-y-2">
                <button
                  onClick={() => setActiveTab("overview")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                    activeTab === "overview"
                      ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <BarChart3 className="w-5 h-5" />
                  Overview
                </button>
                <button
                  onClick={() => setActiveTab("chat")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                    activeTab === "chat"
                      ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <MessageSquare className="w-5 h-5" />
                  Test Chat
                </button>
                <button
                  onClick={() => setActiveTab("agents")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                    activeTab === "agents"
                      ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <Bot className="w-5 h-5" />
                  AI Agents
                </button>
                <button
                  onClick={() => setActiveTab("training")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                    activeTab === "training"
                      ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <FileText className="w-5 h-5" />
                  Training
                </button>
                <button
                  onClick={() => setActiveTab("integrations")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                    activeTab === "integrations"
                      ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <Globe className="w-5 h-5" />
                  Integrations
                </button>
                <button
                  onClick={() => setActiveTab("analytics")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                    activeTab === "analytics"
                      ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <TrendingUp className="w-5 h-5" />
                  Analytics
                </button>
                <button
                  onClick={() => setActiveTab("profile")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                    activeTab === "profile"
                      ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <Shield className="w-5 h-5" />
                  Profile
                </button>
                <button
                  onClick={() => setActiveTab("settings")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 ${
                    activeTab === "settings"
                      ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <Settings className="w-5 h-5" />
                  Settings
                </button>
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-white/20">
              {activeTab === "overview" && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Dashboard Overview</h2>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-6 rounded-xl">
                      <h3 className="font-bold text-gray-900 mb-4">AI Agents Status</h3>
                      <div className="space-y-3">
                        {agents.length > 0 ? (
                          agents.map((agent) => (
                            <div key={agent.id} className="flex items-center justify-between bg-white p-3 rounded-lg">
                              <div>
                                <div className="font-medium text-gray-900">{agent.name}</div>
                                <div className="text-sm text-gray-600">{agent.total_conversations} conversations</div>
                              </div>
                              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                                agent.training_status === 'trained' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {agent.training_status}
                              </div>
                            </div>
                          ))
                        ) : (
                          <p className="text-gray-600">No AI agents created yet. Click "Create AI Agent" to get started.</p>
                        )}
                      </div>
                    </div>

                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl">
                      <h3 className="font-bold text-gray-900 mb-4">Training Documents</h3>
                      <div className="space-y-3">
                        {documents.length > 0 ? (
                          documents.slice(0, 3).map((doc) => (
                            <div key={doc.id} className="flex items-center justify-between bg-white p-3 rounded-lg">
                              <div>
                                <div className="font-medium text-gray-900 truncate">{doc.filename}</div>
                                <div className="text-sm text-gray-600">{doc.word_count} words</div>
                              </div>
                              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                                doc.status === 'trained' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                              }`}>
                                {doc.status}
                              </div>
                            </div>
                          ))
                        ) : (
                          <p className="text-gray-600">No training documents uploaded yet. Click "Upload Training Data" to add documents.</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "chat" && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Test AI Chat</h2>

                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Agent Selection */}
                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl">
                      <h3 className="font-bold text-gray-900 mb-4">Select AI Agent</h3>
                      <div className="space-y-3">
                        <button
                          onClick={() => setSelectedAgentId(null)}
                          className={`w-full text-left p-3 rounded-lg border-2 transition-all ${
                            selectedAgentId === null
                              ? 'border-purple-500 bg-purple-100'
                              : 'border-gray-200 hover:border-purple-300'
                          }`}
                        >
                          <div className="font-medium">Default Agent</div>
                          <div className="text-sm text-gray-600">Use any available agent</div>
                        </button>
                        {agents.map((agent) => (
                          <button
                            key={agent.id}
                            onClick={() => setSelectedAgentId(agent.id)}
                            className={`w-full text-left p-3 rounded-lg border-2 transition-all ${
                              selectedAgentId === agent.id
                                ? 'border-purple-500 bg-purple-100'
                                : 'border-gray-200 hover:border-purple-300'
                            }`}
                          >
                            <div className="font-medium">{agent.name}</div>
                            <div className="text-sm text-gray-600">{agent.total_conversations} conversations</div>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Chat Interface */}
                    <div className="lg:col-span-2 bg-white rounded-xl shadow-lg">
                      <div className="p-6 border-b border-gray-200">
                        <div className="flex justify-between items-center">
                          <h3 className="font-bold text-gray-900">Chat Test</h3>
                          <button
                            onClick={clearChat}
                            className="text-gray-500 hover:text-gray-700 text-sm"
                          >
                            Clear Chat
                          </button>
                        </div>
                      </div>

                      {/* Messages */}
                      <div className="h-96 overflow-y-auto p-6 space-y-4">
                        {chatMessages.length === 0 ? (
                          <div className="text-center text-gray-500 py-8">
                            <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                            <p>Start a conversation to test your AI agent</p>
                          </div>
                        ) : (
                          chatMessages.map((message, index) => (
                            <div
                              key={index}
                              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                              <div
                                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                                  message.role === 'user'
                                    ? 'bg-purple-500 text-white'
                                    : 'bg-gray-100 text-gray-900'
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
                        {isTyping && (
                          <div className="flex justify-start">
                            <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg">
                              <div className="flex space-x-1">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Input */}
                      <div className="p-6 border-t border-gray-200">
                        <div className="flex gap-3">
                          <input
                            type="text"
                            value={chatInput}
                            onChange={(e) => setChatInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                            placeholder="Type your message to test the AI..."
                            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                            disabled={isTyping}
                          />
                          <button
                            onClick={handleSendMessage}
                            disabled={!chatInput.trim() || isTyping}
                            className="bg-purple-500 text-white px-6 py-2 rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Send
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <h3 className="font-semibold text-blue-900 mb-3">Testing Instructions</h3>
                    <ul className="text-blue-800 text-sm space-y-2">
                      <li>• Select an AI agent from the list or use the default agent</li>
                      <li>• Type your message and press Enter or click Send</li>
                      <li>• Test different scenarios like order inquiries, support requests, or general questions</li>
                      <li>• This is a sandbox environment - conversations won't affect live customer chats</li>
                    </ul>
                  </div>
                </div>
              )}

              {activeTab === "agents" && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">AI Agents</h2>
                  <div className="text-center py-12">
                    <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Create Your First AI Agent</h3>
                    <p className="text-gray-600 mb-6">Train an AI agent with your business knowledge to handle customer conversations.</p>
                    <button className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-8 py-3 rounded-lg font-semibold hover:from-blue-600 hover:to-purple-600 transition-all duration-300">
                      Create AI Agent
                    </button>
                  </div>
                </div>
              )}

              {activeTab === "training" && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Training Data</h2>
                  <div className="text-center py-12">
                    <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Upload Training Documents</h3>
                    <p className="text-gray-600 mb-6">Upload PDFs, DOCX, TXT, or CSV files to train your AI agents.</p>
                    <button className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-8 py-3 rounded-lg font-semibold hover:from-green-600 hover:to-emerald-600 transition-all duration-300">
                      Upload Documents
                    </button>
                  </div>
                </div>
              )}

              {activeTab === "integrations" && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Platform Integrations</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl border border-green-100">
                      <div className="flex items-center mb-4">
                        <MessageSquare className="w-8 h-8 text-green-600 mr-3" />
                        <h3 className="font-bold text-gray-900">WhatsApp</h3>
                      </div>
                      <p className="text-gray-600 mb-4">Connect your WhatsApp Business account</p>
                      <button className="w-full bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 transition-colors">
                        Setup WhatsApp
                      </button>
                    </div>

                    <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-xl border border-blue-100">
                      <div className="flex items-center mb-4">
                        <Facebook className="w-8 h-8 text-blue-600 mr-3" />
                        <h3 className="font-bold text-gray-900">Facebook</h3>
                      </div>
                      <p className="text-gray-600 mb-4">Integrate with Facebook Messenger</p>
                      <button className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-colors">
                        Setup Facebook
                      </button>
                    </div>

                    <div className="bg-gradient-to-r from-pink-50 to-purple-50 p-6 rounded-xl border border-pink-100">
                      <div className="flex items-center mb-4">
                        <Instagram className="w-8 h-8 text-pink-600 mr-3" />
                        <h3 className="font-bold text-gray-900">Instagram</h3>
                      </div>
                      <p className="text-gray-600 mb-4">Handle Instagram DMs automatically</p>
                      <button className="w-full bg-pink-500 text-white py-2 rounded-lg hover:bg-pink-600 transition-colors">
                        Setup Instagram
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "analytics" && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Analytics & Reports</h2>
                  <div className="text-center py-12">
                    <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Analytics Coming Soon</h3>
                    <p className="text-gray-600">Detailed analytics and reporting features are being developed.</p>
                  </div>
                </div>
              )}

              {activeTab === "profile" && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Profile & Account</h2>

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
                            {user?.full_name || "Not provided"}
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Username
                          </label>
                          <div className="bg-white px-3 py-2 rounded-lg border border-gray-200">
                            {user?.username}
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Email Address
                          </label>
                          <div className="bg-white px-3 py-2 rounded-lg border border-gray-200">
                            {user?.email}
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Account Type
                          </label>
                          <div className="bg-white px-3 py-2 rounded-lg border border-gray-200 capitalize">
                            Client Account
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Organization Information */}
                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl">
                      <h3 className="font-bold text-gray-900 mb-6 flex items-center">
                        <Building className="w-5 h-5 mr-2" />
                        Organization Details
                      </h3>

                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Organization Name
                          </label>
                          <div className="bg-white px-3 py-2 rounded-lg border border-gray-200">
                            {organization?.name}
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Domain
                          </label>
                          <div className="bg-white px-3 py-2 rounded-lg border border-gray-200">
                            {organization?.domain}
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Current Plan
                          </label>
                          <div className="bg-white px-3 py-2 rounded-lg border border-gray-200 capitalize">
                            {organization?.plan}
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Monthly Usage
                          </label>
                          <div className="bg-white px-3 py-2 rounded-lg border border-gray-200">
                            {organization?.current_monthly_chats || 0} / {organization?.max_monthly_chats || 0} messages
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Payment & Billing Information */}
                  <div className="mt-8 bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-xl">
                    <h3 className="font-bold text-gray-900 mb-6 flex items-center">
                      <Star className="w-5 h-5 mr-2" />
                      Payment & Billing
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="bg-white p-4 rounded-lg border border-gray-200">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">Current Plan</span>
                          <Star className="w-4 h-4 text-yellow-500" />
                        </div>
                        <div className="text-2xl font-bold text-gray-900 capitalize">
                          {organization?.plan}
                        </div>
                        <div className="text-sm text-gray-600">Active subscription</div>
                      </div>

                      <div className="bg-white p-4 rounded-lg border border-gray-200">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">Monthly Usage</span>
                          <Activity className="w-4 h-4 text-blue-500" />
                        </div>
                        <div className="text-2xl font-bold text-gray-900">
                          {organization?.current_monthly_chats || 0}
                        </div>
                        <div className="text-sm text-gray-600">Messages this month</div>
                      </div>

                      <div className="bg-white p-4 rounded-lg border border-gray-200">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">Next Billing</span>
                          <Clock className="w-4 h-4 text-green-500" />
                        </div>
                        <div className="text-2xl font-bold text-gray-900">
                          {organization?.subscription_end
                            ? new Date(organization.subscription_end).toLocaleDateString()
                            : "N/A"
                          }
                        </div>
                        <div className="text-sm text-gray-600">Subscription renewal</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "settings" && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Account Settings</h2>
                  <p className="text-gray-600">Settings functionality coming soon.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}