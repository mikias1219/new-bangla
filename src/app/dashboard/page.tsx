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
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-gray-900">
              {organization?.name || "Dashboard"}
            </h1>
            <div className="flex items-center gap-4">
              <span className="text-gray-600">
                Plan: <span className="font-semibold capitalize">{organization?.plan}</span>
              </span>
              <button
                onClick={() => router.push("/")}
                className="text-gray-600 hover:text-gray-900"
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
            <nav className="flex">
              {[
                { id: "agents", label: "AI Agents", icon: Bot },
                { id: "documents", label: "Training Data", icon: FileText },
                { id: "analytics", label: "Analytics", icon: BarChart3 },
                { id: "settings", label: "Settings", icon: Settings }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
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
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">AI Agents</h2>
                  <button
                    onClick={createAIAgent}
                    className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
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

                      <div className="flex gap-2">
                        <button
                          onClick={() => testAgent(agent.id)}
                          className="flex-1 flex items-center justify-center gap-2 bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700"
                        >
                          <MessageSquare className="w-4 h-4" />
                          Test Chat
                        </button>
                        <button className="p-2 text-gray-400 hover:text-gray-600">
                          <Settings className="w-4 h-4" />
                        </button>
                  </div>
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