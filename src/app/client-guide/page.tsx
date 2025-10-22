"use client";

import { useState } from "react";
import {
  Book,
  Smartphone,
  MessageSquare,
  Instagram,
  Settings,
  Users,
  BarChart3,
  HelpCircle,
  ExternalLink,
  Copy,
  CheckCircle
} from "lucide-react";

export default function ClientGuide() {
  const [activeTab, setActiveTab] = useState("getting-started");
  const [copiedText, setCopiedText] = useState("");

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(text);
    setTimeout(() => setCopiedText(""), 2000);
  };

  const tabs = [
    { id: "getting-started", label: "Getting Started", icon: Book },
    { id: "whatsapp", label: "WhatsApp", icon: Smartphone },
    { id: "facebook", label: "Facebook", icon: MessageSquare },
    { id: "instagram", label: "Instagram", icon: Instagram },
    { id: "management", label: "Management", icon: Settings },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "support", label: "Support", icon: HelpCircle }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            📚 BanglaChatPro Client Guide
          </h1>
          <p className="text-lg text-gray-600">
            Everything you need to know about managing your AI customer service agent
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                      activeTab === tab.id
                        ? "border-blue-500 text-blue-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-sm p-8">
          {activeTab === "getting-started" && <GettingStartedGuide />}
          {activeTab === "whatsapp" && <WhatsAppGuide copyToClipboard={copyToClipboard} copiedText={copiedText} />}
          {activeTab === "facebook" && <FacebookGuide copyToClipboard={copyToClipboard} copiedText={copiedText} />}
          {activeTab === "instagram" && <InstagramGuide copyToClipboard={copyToClipboard} copiedText={copiedText} />}
          {activeTab === "management" && <ManagementGuide />}
          {activeTab === "analytics" && <AnalyticsGuide />}
          {activeTab === "support" && <SupportGuide />}
        </div>
      </div>
    </div>
  );
}

function GettingStartedGuide() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">🚀 Getting Started with Your AI Agent</h2>

      <div className="space-y-8">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">What is BanglaChatPro?</h3>
          <p className="text-gray-600 mb-4">
            BanglaChatPro is an AI-powered customer service platform that automatically handles customer inquiries
            across WhatsApp, Facebook Messenger, and Instagram. Your AI agent responds in Bangla and can:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-2">
            <li>Answer frequently asked questions</li>
            <li>Check order status</li>
            <li>Provide product information</li>
            <li>Handle customer complaints</li>
            <li>Escalate complex issues to human agents</li>
          </ul>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">How It Works</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">1️⃣</span>
              </div>
              <h4 className="font-semibold mb-2">Customer Messages</h4>
              <p className="text-sm text-gray-600">
                Customers send messages through your social media channels
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">2️⃣</span>
              </div>
              <h4 className="font-semibold mb-2">AI Processes</h4>
              <p className="text-sm text-gray-600">
                AI agent analyzes the message and provides instant responses
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">3️⃣</span>
              </div>
              <h4 className="font-semibold mb-2">Human Override</h4>
              <p className="text-sm text-gray-600">
                Complex issues are automatically escalated to your team
              </p>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Quick Setup Checklist</h3>
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-green-800">Create your AI agent</span>
            </div>
            <div className="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-green-800">Upload training documents</span>
            </div>
            <div className="flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <Settings className="w-5 h-5 text-blue-600" />
              <span className="text-blue-800">Connect social media accounts</span>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
              <Users className="w-5 h-5 text-gray-600" />
              <span className="text-gray-800">Test your AI agent</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function WhatsAppGuide({ copyToClipboard, copiedText }: { copyToClipboard: (text: string) => void, copiedText: string }) {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">📱 WhatsApp Integration</h2>

      <div className="space-y-8">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Setup Process</h3>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h4 className="font-semibold text-blue-900 mb-3">Step-by-Step Guide:</h4>
            <ol className="list-decimal list-inside text-blue-800 space-y-2">
              <li>Go to <a href="https://developers.facebook.com" target="_blank" rel="noopener noreferrer" className="underline">Facebook Developers</a></li>
              <li>Create a new Business App</li>
              <li>Add "WhatsApp" product to your app</li>
              <li>Get your WhatsApp Business Phone Number ID</li>
              <li>Generate an access token</li>
              <li>Enter these details in your BanglaChatPro dashboard</li>
            </ol>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Webhook Configuration</h3>
          <p className="text-gray-600 mb-4">
            Set these webhook URLs in your WhatsApp Business API settings:
          </p>

          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium text-gray-900">Webhook URL</p>
                <code className="text-sm text-gray-600">https://yourdomain.com/api/chat/webhooks/whatsapp</code>
              </div>
              <button
                onClick={() => copyToClipboard("https://yourdomain.com/api/chat/webhooks/whatsapp")}
                className="p-2 text-gray-500 hover:text-gray-700"
              >
                {copiedText === "https://yourdomain.com/api/chat/webhooks/whatsapp" ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium text-gray-900">Verify Token</p>
                <code className="text-sm text-gray-600">your_verify_token_here</code>
              </div>
              <button
                onClick={() => copyToClipboard("your_verify_token_here")}
                className="p-2 text-gray-500 hover:text-gray-700"
              >
                {copiedText === "your_verify_token_here" ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Testing Your Integration</h3>
          <p className="text-gray-600 mb-4">
            Once configured, test your WhatsApp integration:
          </p>
          <ol className="list-decimal list-inside text-gray-600 space-y-2">
            <li>Send a message to your WhatsApp Business number</li>
            <li>Check your BanglaChatPro dashboard for the conversation</li>
            <li>Verify that the AI responds in Bangla</li>
            <li>Test complex queries to ensure proper escalation</li>
          </ol>
        </div>
      </div>
    </div>
  );
}

function FacebookGuide({ copyToClipboard, copiedText }: { copyToClipboard: (text: string) => void, copiedText: string }) {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">📘 Facebook Messenger Integration</h2>

      <div className="space-y-8">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Setup Process</h3>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h4 className="font-semibold text-blue-900 mb-3">Getting Your Facebook Access Token:</h4>
            <ol className="list-decimal list-inside text-blue-800 space-y-2">
              <li>Go to your Facebook Page</li>
              <li>Click "Settings" in the left sidebar</li>
              <li>Click "Messenger" → "Access Tokens"</li>
              <li>Generate a new Page Access Token</li>
              <li>Copy your Page ID from the URL (numbers after /pages/)</li>
            </ol>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Webhook Setup</h3>
          <p className="text-gray-600 mb-4">
            Configure these settings in your Facebook App:
          </p>

          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium text-gray-900">Callback URL</p>
                <code className="text-sm text-gray-600">https://yourdomain.com/api/chat/webhooks/facebook</code>
              </div>
              <button
                onClick={() => copyToClipboard("https://yourdomain.com/api/chat/webhooks/facebook")}
                className="p-2 text-gray-500 hover:text-gray-700"
              >
                {copiedText === "https://yourdomain.com/api/chat/webhooks/facebook" ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium text-gray-900">Verify Token</p>
                <code className="text-sm text-gray-600">your_facebook_verify_token</code>
              </div>
              <button
                onClick={() => copyToClipboard("your_facebook_verify_token")}
                className="p-2 text-gray-500 hover:text-gray-700"
              >
                {copiedText === "your_facebook_verify_token" ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Messenger Features</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-semibold mb-2">Quick Replies</h4>
              <p className="text-sm text-gray-600">
                Your AI can send quick reply buttons for common responses
              </p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-semibold mb-2">Typing Indicators</h4>
              <p className="text-sm text-gray-600">
                Shows typing animation while AI processes responses
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function InstagramGuide({ copyToClipboard, copiedText }: { copyToClipboard: (text: string) => void, copiedText: string }) {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">📷 Instagram Integration</h2>

      <div className="space-y-8">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Instagram Business Account</h3>
          <div className="bg-pink-50 border border-pink-200 rounded-lg p-6">
            <h4 className="font-semibold text-pink-900 mb-3">Requirements:</h4>
            <ul className="list-disc list-inside text-pink-800 space-y-2">
              <li>Instagram Business or Creator account</li>
              <li>Linked Facebook Page</li>
              <li>Instagram Basic Display API access</li>
              <li>Uses same Facebook access token</li>
            </ul>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Setup Steps</h3>
          <ol className="list-decimal list-inside text-gray-600 space-y-3">
            <li>
              <strong>Convert to Business Account:</strong> Go to Instagram settings → Account → Switch to Professional Account → Business
            </li>
            <li>
              <strong>Connect Facebook Page:</strong> Link your Instagram to a Facebook Page during setup
            </li>
            <li>
              <strong>Get Account ID:</strong> Use Facebook Graph API Explorer to find your Instagram Business Account ID
            </li>
            <li>
              <strong>Configure Webhook:</strong> Set the Instagram webhook URL in your Facebook App
            </li>
          </ol>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Webhook URL</h3>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">Instagram Webhook</p>
              <code className="text-sm text-gray-600">https://yourdomain.com/api/chat/webhooks/instagram</code>
            </div>
            <button
              onClick={() => copyToClipboard("https://yourdomain.com/api/chat/webhooks/instagram")}
              className="p-2 text-gray-500 hover:text-gray-700"
            >
              {copiedText === "https://yourdomain.com/api/chat/webhooks/instagram" ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ManagementGuide() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">⚙️ Managing Your AI Agent</h2>

      <div className="space-y-8">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Training Your AI Agent</h3>
          <p className="text-gray-600 mb-4">
            Upload documents to train your AI agent with your business knowledge:
          </p>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <h4 className="font-semibold text-gray-900 mb-3">Supported File Types:</h4>
            <div className="grid md:grid-cols-2 gap-4">
              <ul className="list-disc list-inside text-gray-600">
                <li>PDF documents</li>
                <li>Word documents (.docx)</li>
                <li>Text files (.txt)</li>
              </ul>
              <ul className="list-disc list-inside text-gray-600">
                <li>CSV files</li>
                <li>RTF files</li>
                <li>PowerPoint presentations</li>
              </ul>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">AI Agent Settings</h3>
          <div className="space-y-4">
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-semibold mb-2">Response Personality</h4>
              <p className="text-sm text-gray-600">
                Configure how your AI responds - professional, friendly, or expert tone
              </p>
            </div>
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-semibold mb-2">Response Limits</h4>
              <p className="text-sm text-gray-600">
                Set maximum response length and token usage
              </p>
            </div>
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-semibold mb-2">Language Settings</h4>
              <p className="text-sm text-gray-600">
                AI responds exclusively in Bangla by default
              </p>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Integration Management</h3>
          <p className="text-gray-600 mb-4">
            Enable or disable integrations as needed:
          </p>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="border border-gray-200 rounded-lg p-4 text-center">
              <Smartphone className="w-8 h-8 text-green-500 mx-auto mb-2" />
              <h4 className="font-semibold">WhatsApp</h4>
              <p className="text-sm text-gray-600">Toggle on/off</p>
            </div>
            <div className="border border-gray-200 rounded-lg p-4 text-center">
              <MessageSquare className="w-8 h-8 text-blue-500 mx-auto mb-2" />
              <h4 className="font-semibold">Facebook</h4>
              <p className="text-sm text-gray-600">Toggle on/off</p>
            </div>
            <div className="border border-gray-200 rounded-lg p-4 text-center">
              <Instagram className="w-8 h-8 text-pink-500 mx-auto mb-2" />
              <h4 className="font-semibold">Instagram</h4>
              <p className="text-sm text-gray-600">Toggle on/off</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function AnalyticsGuide() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">📊 Understanding Analytics</h2>

      <div className="space-y-8">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Key Metrics to Monitor</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-2">Total Conversations</h4>
              <p className="text-sm text-blue-800">
                Total number of customer interactions handled by your AI
              </p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-semibold text-green-900 mb-2">Response Time</h4>
              <p className="text-sm text-green-800">
                Average time for AI to respond to customer messages
              </p>
            </div>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h4 className="font-semibold text-purple-900 mb-2">Confidence Score</h4>
              <p className="text-sm text-purple-800">
                How confident the AI is in its responses (higher is better)
              </p>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h4 className="font-semibold text-red-900 mb-2">Escalations</h4>
              <p className="text-sm text-red-800">
                Conversations that required human intervention
              </p>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Platform Performance</h3>
          <p className="text-gray-600 mb-4">
            See how your AI performs on different social media platforms:
          </p>
          <div className="overflow-x-auto">
            <table className="min-w-full border border-gray-200 rounded-lg">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left font-semibold">Platform</th>
                  <th className="px-4 py-2 text-left font-semibold">Conversations</th>
                  <th className="px-4 py-2 text-left font-semibold">Avg Response Time</th>
                  <th className="px-4 py-2 text-left font-semibold">Satisfaction Rate</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-t border-gray-200">
                  <td className="px-4 py-2 flex items-center gap-2">
                    <Smartphone className="w-4 h-4 text-green-500" />
                    WhatsApp
                  </td>
                  <td className="px-4 py-2">1,245</td>
                  <td className="px-4 py-2">3.2s</td>
                  <td className="px-4 py-2">94%</td>
                </tr>
                <tr className="border-t border-gray-200">
                  <td className="px-4 py-2 flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-blue-500" />
                    Facebook
                  </td>
                  <td className="px-4 py-2">856</td>
                  <td className="px-4 py-2">2.8s</td>
                  <td className="px-4 py-2">96%</td>
                </tr>
                <tr className="border-t border-gray-200">
                  <td className="px-4 py-2 flex items-center gap-2">
                    <Instagram className="w-4 h-4 text-pink-500" />
                    Instagram
                  </td>
                  <td className="px-4 py-2">432</td>
                  <td className="px-4 py-2">3.5s</td>
                  <td className="px-4 py-2">92%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Customer Satisfaction</h3>
          <p className="text-gray-600 mb-4">
            Monitor how satisfied your customers are with AI responses:
          </p>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h4 className="font-semibold mb-4">Rating Distribution</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">5 Stars</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div className="bg-yellow-400 h-2 rounded-full" style={{width: '65%'}}></div>
                    </div>
                    <span className="text-sm font-medium w-8 text-right">65%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">4 Stars</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div className="bg-yellow-400 h-2 rounded-full" style={{width: '25%'}}></div>
                    </div>
                    <span className="text-sm font-medium w-8 text-right">25%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">3 Stars</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div className="bg-yellow-400 h-2 rounded-full" style={{width: '8%'}}></div>
                    </div>
                    <span className="text-sm font-medium w-8 text-right">8%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">1-2 Stars</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div className="bg-red-400 h-2 rounded-full" style={{width: '2%'}}></div>
                    </div>
                    <span className="text-sm font-medium w-8 text-right">2%</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h4 className="font-semibold mb-4">Improvement Suggestions</h4>
              <div className="space-y-3">
                <div className="p-3 bg-blue-50 border border-blue-200 rounded">
                  <p className="text-sm text-blue-800">
                    <strong>Training needed:</strong> Product information queries have lower confidence scores
                  </p>
                </div>
                <div className="p-3 bg-green-50 border border-green-200 rounded">
                  <p className="text-sm text-green-800">
                    <strong>Great performance:</strong> Order status inquiries are handled very well
                  </p>
                </div>
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                  <p className="text-sm text-yellow-800">
                    <strong>Consider:</strong> Add more training data for complex technical questions
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SupportGuide() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">🆘 Getting Help & Support</h2>

      <div className="space-y-8">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Contact Support</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h4 className="font-semibold text-blue-900 mb-3">Technical Support</h4>
              <p className="text-blue-800 mb-3">
                For technical issues, integration problems, or system errors
              </p>
              <div className="space-y-2">
                <p className="text-sm">
                  <strong>Email:</strong> support@banglachatpro.com
                </p>
                <p className="text-sm">
                  <strong>Phone:</strong> +880 1234-567890
                </p>
                <p className="text-sm">
                  <strong>Response time:</strong> Within 2 hours
                </p>
              </div>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h4 className="font-semibold text-green-900 mb-3">AI Training Support</h4>
              <p className="text-green-800 mb-3">
                Help with training your AI agent and improving responses
              </p>
              <div className="space-y-2">
                <p className="text-sm">
                  <strong>Email:</strong> training@banglachatpro.com
                </p>
                <p className="text-sm">
                  <strong>Live Chat:</strong> Available in dashboard
                </p>
                <p className="text-sm">
                  <strong>Response time:</strong> Within 4 hours
                </p>
              </div>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Common Issues & Solutions</h3>
          <div className="space-y-4">
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-2">AI Not Responding</h4>
              <p className="text-gray-600 mb-2">
                Check if your OpenAI API key is valid and has sufficient credits
              </p>
              <p className="text-sm text-gray-500">
                Solution: Verify your API key in system settings and check usage limits
              </p>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-2">Webhook Failures</h4>
              <p className="text-gray-600 mb-2">
                Social media webhooks not receiving messages
              </p>
              <p className="text-sm text-gray-500">
                Solution: Check webhook URLs and verify tokens in your social media developer consoles
              </p>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-2">Low AI Confidence</h4>
              <p className="text-gray-600 mb-2">
                AI responses have low confidence scores
              </p>
              <p className="text-sm text-gray-500">
                Solution: Upload more training documents and refine your AI agent's knowledge base
              </p>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Resources</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <a
              href="/client-guide"
              className="flex items-center gap-3 p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Book className="w-6 h-6 text-blue-500" />
              <div>
                <h4 className="font-semibold">Complete Client Guide</h4>
                <p className="text-sm text-gray-600">Detailed documentation</p>
              </div>
              <ExternalLink className="w-4 h-4 text-gray-400 ml-auto" />
            </a>

            <a
              href="/integration-setup"
              className="flex items-center gap-3 p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Settings className="w-6 h-6 text-green-500" />
              <div>
                <h4 className="font-semibold">Integration Setup</h4>
                <p className="text-sm text-gray-600">Step-by-step integration</p>
              </div>
              <ExternalLink className="w-4 h-4 text-gray-400 ml-auto" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
