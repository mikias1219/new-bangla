"use client";

import { useState, useEffect, useCallback } from "react";
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
  BarChart3
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

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("agents");
  const [agents, setAgents] = useState<AIAgent[]>([]);
  const [documents, setDocuments] = useState<TrainingDocument[]>([]);
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const router = useRouter();

  const checkAuth = useCallback(async () => {
    try {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

      // Load dashboard data
      await Promise.all([
        loadOrganization(),
        loadAIAgents(),
        loadDocuments()
      ]);
    } catch (error) {
      console.error("Auth check failed:", error);
      router.push("/login");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const loadOrganization = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("/api/organizations/my", {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setOrganization(data);
      }
    } catch (error) {
      console.error("Failed to load organization:", error);
    }
  };

  const loadAIAgents = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("/api/organizations/ai-agents", {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setAgents(data);
      }
    } catch (error) {
      console.error("Failed to load AI agents:", error);
    }
  };

  const loadDocuments = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("/api/organizations/documents", {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      }
    } catch (error) {
      console.error("Failed to load documents:", error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const token = localStorage.getItem("token");
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/api/organizations/documents/upload", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });

      if (response.ok) {
        alert("Document uploaded successfully! Processing will begin shortly.");
        await loadDocuments(); // Refresh documents list
      } else {
        const error = await response.json();
        alert(`Upload failed: ${error.detail}`);
      }
    } catch (error) {
      console.error("Upload error:", error);
      alert("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const createAIAgent = async () => {
    const name = prompt("Enter AI Agent name:");
    const description = prompt("Enter AI Agent description:");

    if (!name || !description) return;

    try {
      const token = localStorage.getItem("token");
      const response = await fetch("/api/organizations/ai-agents", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ name, description })
      });

      if (response.ok) {
        alert("AI Agent created successfully!");
        await loadAIAgents();
      } else {
        const error = await response.json();
        alert(`Failed to create agent: ${error.detail}`);
      }
    } catch (error) {
      console.error("Error creating agent:", error);
      alert("Failed to create AI agent");
    }
  };

  const testAgent = (agentId: number) => {
    // Open chat interface for this agent
    router.push(`/chat?agent=${agentId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center h-auto sm:h-16 gap-2 py-4 sm:py-0">
            <h1 className="text-xl sm:text-2xl font-bold text-gray-900">
              {organization?.name || "Dashboard"}
            </h1>
            <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
              <span className="text-gray-600 text-sm sm:text-base">
                Plan: <span className="font-semibold capitalize">{organization?.plan}</span>
              </span>
              <button
                onClick={() => router.push("/")}
                className="text-gray-600 hover:text-gray-900 text-sm sm:text-base"
              >
                ← Back to Home
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Usage Stats */}
        {organization && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Usage Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <Users className="w-8 h-8 text-blue-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-blue-600">AI Agents</p>
                    <p className="text-2xl font-bold text-blue-900">
                      {agents.length}/{organization.max_ai_agents}
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <MessageSquare className="w-8 h-8 text-green-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-green-600">Monthly Chats</p>
                    <p className="text-2xl font-bold text-green-900">
                      {organization.current_monthly_chats}/{organization.max_monthly_chats}
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <FileText className="w-8 h-8 text-purple-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-purple-600">Documents</p>
                    <p className="text-2xl font-bold text-purple-900">{documents.length}</p>
                  </div>
                </div>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <TrendingUp className="w-8 h-8 text-yellow-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-yellow-600">Usage</p>
                    <p className="text-2xl font-bold text-yellow-900">
                      {organization.max_monthly_chats > 0 ?
                        Math.round((organization.current_monthly_chats / organization.max_monthly_chats) * 100) : 0}%
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex overflow-x-auto">
              {[
                { id: "agents", label: "AI Agents", icon: Bot },
                { id: "documents", label: "Training Data", icon: FileText },
                { id: "integrations", label: "Integrations", icon: Settings },
                { id: "analytics", label: "Analytics", icon: BarChart3 },
                { id: "settings", label: "Settings", icon: Settings }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 sm:px-6 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap min-w-max ${
                    activeTab === tab.id
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* AI Agents Tab */}
            {activeTab === "agents" && (
              <div>
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">AI Agents</h2>
                  <button
                    onClick={createAIAgent}
                    className="flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 w-full sm:w-auto"
                  >
                    <Plus className="w-4 h-4" />
                    Create Agent
                  </button>
            </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {agents.map((agent) => (
                    <div key={agent.id} className="bg-gray-50 rounded-lg p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                          <p className="text-gray-600 text-sm">{agent.description}</p>
                  </div>
                        <div className={`px-2 py-1 rounded text-xs font-medium ${
                          agent.training_status === "trained"
                            ? "bg-green-100 text-green-800"
                            : agent.training_status === "training"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-red-100 text-red-800"
                        }`}>
                          {agent.training_status}
                        </div>
                      </div>

                      <div className="space-y-2 mb-4">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Conversations</span>
                          <span className="font-medium">{agent.total_conversations}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {agent.whatsapp_enabled && (
                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">WhatsApp</span>
                          )}
                          {agent.facebook_enabled && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Facebook</span>
                          )}
                        </div>
                      </div>

                      <div className="flex flex-col sm:flex-row gap-2">
                        <button
                          onClick={() => testAgent(agent.id)}
                          className="flex-1 flex items-center justify-center gap-2 bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700"
                        >
                          <MessageSquare className="w-4 h-4" />
                          Test Chat
                        </button>
                        <button className="p-2 text-gray-400 hover:text-gray-600 self-center sm:self-auto">
                          <Settings className="w-4 h-4" />
                        </button>
                      </div>

                      {agent.training_status === "trained" && (
                        <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                          <p className="text-xs text-green-700 mb-2">
                            ✅ Agent is ready! Test it before integrating with social media.
                          </p>
                          <button
                            onClick={() => router.push(`/integration-setup?agent=${agent.id}`)}
                            className="w-full text-xs bg-green-600 text-white px-3 py-2 rounded hover:bg-green-700"
                          >
                            Setup Social Media Integration
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {agents.length === 0 && (
                  <div className="text-center py-12">
                    <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No AI Agents Yet</h3>
                    <p className="text-gray-600 mb-4">Create your first AI agent to start chatting with your customers.</p>
                    <button
                      onClick={createAIAgent}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                    >
                      Create Your First Agent
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Training Documents Tab */}
            {activeTab === "documents" && (
          <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">Training Documents</h2>
          <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 cursor-pointer">
                      <Upload className="w-4 h-4" />
                      {uploading ? "Uploading..." : "Upload Document"}
              <input
                        type="file"
                        accept=".pdf,.doc,.docx,.txt,.csv"
                        onChange={handleFileUpload}
                        className="hidden"
                        disabled={uploading}
                      />
            </label>
          </div>
        </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <h3 className="font-medium text-blue-900 mb-2">Supported File Types</h3>
                  <p className="text-blue-700 text-sm">
                    Upload PDF, Word documents (.doc, .docx), text files (.txt), or CSV files to train your AI agents.
                    Documents are processed automatically and used to provide accurate responses.
                  </p>
      </div>

                <div className="space-y-4">
                  {documents.map((doc) => (
                    <div key={doc.id} className="bg-white border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <FileText className="w-8 h-8 text-gray-400" />
                          <div>
                            <h3 className="font-medium text-gray-900">{doc.filename}</h3>
                            <p className="text-sm text-gray-600">
                              {doc.word_count} words • Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}
                            </p>
                          </div>
          </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            doc.status === "completed"
                              ? "bg-green-100 text-green-800"
                              : doc.status === "processing"
                              ? "bg-yellow-100 text-yellow-800"
                              : "bg-red-100 text-red-800"
                          }`}>
                            {doc.status}
                          </span>
                          {doc.trained_at && (
                            <span className="text-xs text-gray-500">
                              Trained {new Date(doc.trained_at).toLocaleDateString()}
                            </span>
                          )}
                        </div>
            </div>
          </div>
        ))}
                </div>

                {documents.length === 0 && (
                  <div className="text-center py-12">
                    <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Training Documents</h3>
                    <p className="text-gray-600 mb-4">Upload documents to train your AI agents with your knowledge base.</p>
                  </div>
                )}
              </div>
            )}

            {/* Integrations Tab */}
            {activeTab === "integrations" && (
              <div>
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">Social Media Integrations</h2>
                  <p className="text-gray-600">
                    Connect your business accounts to enable AI-powered responses on WhatsApp, Facebook, and Instagram.
                    Your AI agents will automatically respond to customer messages based on your training data.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                  {/* WhatsApp Integration */}
                  <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center mb-4">
                      <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                        <MessageSquare className="w-6 h-6 text-green-600" />
                      </div>
                      <div className="ml-4">
                        <h3 className="text-lg font-semibold text-gray-900">WhatsApp Business</h3>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Most Popular
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-600 text-sm mb-4">
                      Connect your WhatsApp Business account to enable AI responses for customer inquiries, orders, and support.
                    </p>
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center text-sm text-gray-600">
                        <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                        24/7 automated responses
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                        Bangla language support
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                        Message templates
                      </div>
                    </div>
                    <button
                      onClick={() => window.open('/integration-setup?platform=whatsapp', '_blank')}
                      className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Setup WhatsApp
                    </button>
                  </div>

                  {/* Facebook Integration */}
                  <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center mb-4">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                        </svg>
                      </div>
                      <div className="ml-4">
                        <h3 className="text-lg font-semibold text-gray-900">Facebook Messenger</h3>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          Business Pages
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-600 text-sm mb-4">
                      Connect your Facebook Business Page to handle customer messages through Messenger.
                    </p>
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center text-sm text-gray-600">
                        <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                        Page inbox automation
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                        Customer support
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                        Lead generation
                      </div>
                    </div>
                    <button
                      onClick={() => window.open('/integration-setup?platform=facebook', '_blank')}
                      className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Setup Facebook
                    </button>
                  </div>

                  {/* Instagram Integration */}
                  <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center mb-4">
                      <div className="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center">
                        <svg className="w-6 h-6 text-pink-600" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12.017 0C8.396 0 7.909.016 6.695.072 5.48.127 4.63.245 3.892.467c-.825.234-1.527.547-2.235 1.254C.95 2.428.637 3.13.403 3.955.245 4.693.127 5.543.072 6.758.016 7.972 0 8.459 0 12.08s.016 4.108.072 5.322c.055 1.215.173 2.065.331 2.803.234.825.547 1.527 1.254 2.235.708.708 1.41 1.021 2.235 1.255.738.222 1.588.34 2.803.395C7.909 23.984 8.396 24 12.017 24s4.108-.016 5.322-.072c1.215-.055 2.065-.173 2.803-.331.825-.234 1.527-.547 2.235-1.254.708-.708 1.021-1.41 1.255-2.235.222-.738.34-1.588.395-2.803.056-1.215.072-1.702.072-5.322s-.016-4.108-.072-5.322c-.055-1.215-.173-2.065-.331-2.803-.234-.825-.547-1.527-1.254-2.235C21.592.951 20.89.638 20.065.403c-.738-.222-1.588-.34-2.803-.395C16.125.016 15.638 0 12.017 0zm0 5.351c3.664 0 6.63 2.966 6.63 6.63s-2.966 6.63-6.63 6.63-6.63-2.966-6.63-6.63 2.966-6.63 6.63-6.63zm0 10.949c2.39 0 4.329-1.939 4.329-4.329s-1.939-4.329-4.329-4.329-4.329 1.939-4.329 4.329 1.939 4.329 4.329 4.329zm8.507-11.286c-.826 0-1.497-.671-1.497-1.497s.671-1.497 1.497-1.497 1.497.671 1.497 1.497-.671 1.497-1.497 1.497z"/>
                        </svg>
                      </div>
                      <div className="ml-4">
                        <h3 className="text-lg font-semibold text-gray-900">Instagram Direct</h3>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-pink-100 text-pink-800">
                          Business Accounts
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-600 text-sm mb-4">
                      Connect your Instagram Business account to handle direct messages and customer inquiries.
                    </p>
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center text-sm text-gray-600">
                        <span className="w-2 h-2 bg-pink-500 rounded-full mr-2"></span>
                        DM automation
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <span className="w-2 h-2 bg-pink-500 rounded-full mr-2"></span>
                        Brand engagement
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <span className="w-2 h-2 bg-pink-500 rounded-full mr-2"></span>
                        Customer service
                      </div>
                    </div>
                    <button
                      onClick={() => window.open('/integration-setup?platform=instagram', '_blank')}
                      className="w-full bg-pink-600 text-white px-4 py-2 rounded-lg hover:bg-pink-700 transition-colors"
                    >
                      Setup Instagram
                    </button>
                  </div>
                </div>

                {/* Integration Guide */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Settings className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-blue-900 mb-2">How Integration Works</h3>
                      <div className="text-blue-700 space-y-2">
                        <p><strong>1. Setup:</strong> Click on any integration above to get step-by-step setup instructions.</p>
                        <p><strong>2. Connect:</strong> Link your business accounts using API keys and access tokens.</p>
                        <p><strong>3. Assign AI Agents:</strong> Choose which AI agent handles messages from each platform.</p>
                        <p><strong>4. Train & Go Live:</strong> Your AI agent will automatically respond to customer messages based on your training data.</p>
                      </div>
                      <div className="mt-4">
                        <button
                          onClick={() => router.push('/client-guide')}
                          className="text-blue-600 hover:text-blue-800 font-medium underline"
                        >
                          View Complete Setup Guide →
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Analytics Tab */}
            {activeTab === "analytics" && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-6">Analytics</h2>

                {/* Analytics content will be implemented */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                  <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-blue-100 text-sm font-medium">Total Conversations</p>
                        <p className="text-2xl font-bold">0</p>
                      </div>
                      <MessageSquare className="w-8 h-8 text-blue-200" />
            </div>
          </div>

                  <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-green-100 text-sm font-medium">Messages This Month</p>
                        <p className="text-2xl font-bold">0</p>
                      </div>
                      <TrendingUp className="w-8 h-8 text-green-200" />
                    </div>
      </div>

                  <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-purple-100 text-sm font-medium">Avg. Response Time</p>
                        <p className="text-2xl font-bold">-</p>
                      </div>
                      <BarChart3 className="w-8 h-8 text-purple-200" />
                    </div>
        </div>
      </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Platform Usage */}
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h3 className="font-medium text-gray-900 mb-4">Platform Usage</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600">Web Chat</span>
                        <span className="font-medium">0%</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600">WhatsApp</span>
                        <span className="font-medium">0%</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600">Facebook</span>
                        <span className="font-medium">0%</span>
                      </div>
                    </div>
                  </div>

                  {/* Recent Activity */}
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h3 className="font-medium text-gray-900 mb-4">Recent Conversations</h3>
                    <div className="space-y-3">
                      <p className="text-gray-500 text-sm">No recent conversations</p>
    </div>
      </div>
      </div>
    </div>
            )}

            {/* Settings Tab */}
            {activeTab === "settings" && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-6">Organization Settings</h2>
                {organization && (
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h3 className="font-medium text-gray-900 mb-4">Organization Information</h3>
                    <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Organization Name</dt>
                        <dd className="text-sm text-gray-900">{organization.name}</dd>
      </div>
          <div>
                        <dt className="text-sm font-medium text-gray-500">Domain</dt>
                        <dd className="text-sm text-gray-900">{organization.domain}</dd>
          </div>
          <div>
                        <dt className="text-sm font-medium text-gray-500">Plan</dt>
                        <dd className="text-sm text-gray-900 capitalize">{organization.plan}</dd>
          </div>
          <div>
                        <dt className="text-sm font-medium text-gray-500">Max Users</dt>
                        <dd className="text-sm text-gray-900">{organization.max_users}</dd>
                      </div>
                    </dl>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}