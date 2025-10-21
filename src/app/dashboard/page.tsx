"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { MessageSquare, CreditCard, Settings, LogOut, Shield } from "lucide-react";
import VoiceChat, { speakAiResponse } from "../../components/voice/VoiceChat";
import SocialMediaIntegration, { createShareableContent } from "../../components/chat/SocialMediaIntegration";

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  is_superuser?: boolean;
}

interface Subscription {
  plan: string;
  status: string;
  trial_end?: string;
}

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [activeTab, setActiveTab] = useState("chat");
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    // TODO: Fetch user data and subscription
    fetchUserData();
  }, [router]);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;

      // Fetch user data from API
      const userResponse = await fetch("/api/users/me", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (userResponse.ok) {
        const userData = await userResponse.json();
        setUser(userData);
      } else {
        // Fallback to mock data if API fails
        setUser({
          id: 1,
          email: "user@example.com",
          username: "johndoe",
          full_name: "John Doe",
          is_superuser: false
        });
      }

      // Fetch subscription data
      const subscriptionResponse = await fetch("/api/subscriptions/current", {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (subscriptionResponse.ok) {
        const subscriptionData = await subscriptionResponse.json();
        setSubscription({
          plan: subscriptionData.plan || "free",
          status: subscriptionData.status || "trialing",
          trial_end: subscriptionData.trial_end
        });
      } else {
        // Fallback to mock subscription data
        setSubscription({
          plan: "free",
          status: "trialing",
          trial_end: "2024-02-01"
        });
      }
    } catch (error) {
      console.error("Failed to fetch user data:", error);
      // Fallback to mock data
      setUser({
        id: 1,
        email: "user@example.com",
        username: "johndoe",
        full_name: "John Doe",
        is_superuser: false
      });
      setSubscription({
        plan: "free",
        status: "trialing",
        trial_end: "2024-02-01"
      });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/");
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
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
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <div className="flex items-center gap-4">
              <span className="text-gray-700">Welcome, {user.full_name}</span>
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
                  onClick={() => setActiveTab("chat")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors ${
                    activeTab === "chat"
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <MessageSquare className="w-5 h-5" />
                  AI Chat
                </button>
                <button
                  onClick={() => setActiveTab("subscription")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors ${
                    activeTab === "subscription"
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <CreditCard className="w-5 h-5" />
                  Subscription
                </button>
                <button
                  onClick={() => setActiveTab("settings")}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors ${
                    activeTab === "settings"
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <Settings className="w-5 h-5" />
                  Settings
                </button>
                {user?.is_superuser && (
                  <button
                    onClick={() => router.push("/admin")}
                    className="w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors text-red-700 hover:bg-red-50"
                  >
                    <Shield className="w-5 h-5" />
                    Admin Panel
                  </button>
                )}
              </nav>
            </div>

            {/* Subscription Status */}
            {subscription && (
              <div className="bg-white rounded-lg shadow p-6 mt-6">
                <h3 className="font-semibold text-gray-900 mb-3">Current Plan</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Plan:</span>
                    <span className="font-medium capitalize">{subscription.plan}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Status:</span>
                    <span className={`font-medium capitalize ${
                      subscription.status === 'active' ? 'text-green-600' :
                      subscription.status === 'trialing' ? 'text-blue-600' : 'text-gray-600'
                    }`}>
                      {subscription.status}
                    </span>
                  </div>
                  {subscription.trial_end && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Trial ends:</span>
                      <span className="font-medium">{subscription.trial_end}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {activeTab === "chat" && <ChatInterface />}
            {activeTab === "subscription" && <SubscriptionManager />}
            {activeTab === "settings" && <SettingsPanel user={user} />}
          </div>
        </div>
      </div>
    </div>
  );
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [voiceMode, setVoiceMode] = useState(false);
  const [socialMode, setSocialMode] = useState(false);
  const [lastAiResponse, setLastAiResponse] = useState("");

  const sendMessage = async (messageText?: string) => {
    const messageToSend = messageText || inputMessage;
    if (!messageToSend.trim()) return;

    const userMessage: ChatMessage = { role: "user", content: messageToSend };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("No authentication token found");
      }

      const response = await fetch("/api/ai/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: messageToSend,
          conversation_id: `conv_${Date.now()}`,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage: ChatMessage = {
          role: "assistant",
          content: data.response,
        };
        setMessages(prev => [...prev, aiMessage]);
        setLastAiResponse(data.response);

        // Speak the AI response if voice mode is enabled
        if (voiceMode) {
          speakAiResponse(data.response);
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to get AI response");
      }
    } catch (error) {
      console.error("Failed to send message:", error);
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : "Unknown error"}. Please try again.`,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceMessage = (voiceMessage: string) => {
    sendMessage(voiceMessage);
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">AI Chat</h2>
            <p className="text-gray-600">Chat with our intelligent AI assistant</p>
          </div>
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm text-gray-600">
              <input
                type="checkbox"
                checked={voiceMode}
                onChange={(e) => setVoiceMode(e.target.checked)}
                className="rounded"
              />
              Voice Mode
            </label>
            <label className="flex items-center gap-2 text-sm text-gray-600">
              <input
                type="checkbox"
                checked={socialMode}
                onChange={(e) => setSocialMode(e.target.checked)}
                className="rounded"
              />
              Social Share
            </label>
          </div>
        </div>
      </div>

      <div className="h-96 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-20">
            <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Start a conversation with our AI assistant</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-900"
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-2 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="p-6 border-t border-gray-200">
        <div className="flex gap-4">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>

      {/* Voice Chat Component */}
      {voiceMode && (
        <VoiceChat
          onVoiceMessage={handleVoiceMessage}
          isLoading={isLoading}
        />
      )}

      {/* Social Media Integration */}
      {socialMode && lastAiResponse && (
        <SocialMediaIntegration
          message={createShareableContent(lastAiResponse, "AI Response from Bangla Chat Pro")}
          onShare={(platform, message) => {
            console.log(`Sharing to ${platform}:`, message);
            // Here you would integrate with actual social media APIs
          }}
        />
      )}
    </div>
  );
}

function SubscriptionManager() {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">Subscription Management</h2>
        <p className="text-gray-600">Manage your subscription and billing</p>
      </div>
      <div className="p-6">
        <p className="text-gray-600">Subscription management features will be available soon.</p>
      </div>
    </div>
  );
}

function SettingsPanel({ user }: { user: User }) {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">Account Settings</h2>
        <p className="text-gray-600">Manage your account information</p>
      </div>
      <div className="p-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Full Name</label>
            <input
              type="text"
              defaultValue={user.full_name}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              defaultValue={user.email}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Username</label>
            <input
              type="text"
              defaultValue={user.username}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
