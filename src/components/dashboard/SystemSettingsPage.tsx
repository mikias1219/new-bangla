"use client";

import { useState } from "react";
import { Settings, Key, Shield, Save, Globe, Zap } from "lucide-react";
import DashboardBreadcrumb from "./DashboardBreadcrumb";

export default function SystemSettingsPage() {
  const [activeTab, setActiveTab] = useState<"api-integration" | "handoff-rules" | "security">("api-integration");
  const [apiEndpoint, setApiEndpoint] = useState("https://api.example.com/v1");
  const [apiKey, setApiKey] = useState("sk-******************************");
  const [maxUnsuccessfulResponses, setMaxUnsuccessfulResponses] = useState(2);

  const breadcrumbItems = [
    { label: "Dashboard" },
    { label: "System Settings" }
  ];

  const tabs = [
    { id: "api-integration", label: "API Integration", icon: Globe },
    { id: "handoff-rules", label: "Handoff Rules", icon: Zap },
    { id: "security", label: "Security", icon: Shield }
  ];

  const handleSaveSettings = () => {
    // In a real app, this would save to backend
    console.log("Saving settings:", {
      apiEndpoint,
      apiKey,
      maxUnsuccessfulResponses
    });
    alert("Settings saved successfully!");
  };

  return (
    <div className="p-6">
      <DashboardBreadcrumb items={breadcrumbItems} />

      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">System Settings</h1>
        <p className="text-gray-600">Configure system-wide settings and integrations</p>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {/* API Integration Tab */}
          {activeTab === "api-integration" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Backend API Integration</h3>
                <p className="text-gray-600 mb-6">
                  Configure the backend API endpoint and authentication for real-time information retrieval.
                </p>

                <div className="space-y-4">
                  <div>
                    <label htmlFor="api-endpoint" className="block text-sm font-medium text-gray-700 mb-2">
                      Backend API Endpoint URL
                    </label>
                    <input
                      type="url"
                      id="api-endpoint"
                      value={apiEndpoint}
                      onChange={(e) => setApiEndpoint(e.target.value)}
                      placeholder="https://api.example.com/v1"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <p className="text-sm text-gray-500 mt-1">
                      The base URL for your backend API that provides customer data, orders, and other information.
                    </p>
                  </div>

                  <div>
                    <label htmlFor="api-key" className="block text-sm font-medium text-gray-700 mb-2">
                      API Key
                    </label>
                    <div className="relative">
                      <input
                        type="password"
                        id="api-key"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="sk-******************************"
                        className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <Key className="w-4 h-4 absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      Your API authentication key. Keep this secure and never share it publicly.
                    </p>
                  </div>

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <Globe className="w-5 h-5 text-blue-400" />
                      </div>
                      <div className="ml-3">
                        <h4 className="text-sm font-medium text-blue-800">API Status</h4>
                        <div className="mt-2 text-sm text-blue-700">
                          <p>✅ Connection successful</p>
                          <p>✅ Authentication verified</p>
                          <p>✅ Real-time data available</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Handoff Rules Tab */}
          {activeTab === "handoff-rules" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Human Handoff Configuration</h3>
                <p className="text-gray-600 mb-6">
                  Set the rules for when AI conversations should be escalated to human agents.
                </p>

                <div className="space-y-4">
                  <div>
                    <label htmlFor="max-responses" className="block text-sm font-medium text-gray-700 mb-2">
                      Max AI Unsuccessful Responses Before Handoff
                    </label>
                    <div className="max-w-xs">
                      <input
                        type="number"
                        id="max-responses"
                        min="1"
                        max="10"
                        value={maxUnsuccessfulResponses}
                        onChange={(e) => setMaxUnsuccessfulResponses(Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      After this many unsuccessful AI responses, the conversation will be automatically handed off to a human agent.
                    </p>
                  </div>

                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <Zap className="w-5 h-5 text-yellow-400" />
                      </div>
                      <div className="ml-3">
                        <h4 className="text-sm font-medium text-yellow-800">Current Setting: {maxUnsuccessfulResponses} responses</h4>
                        <div className="mt-2 text-sm text-yellow-700">
                          <p>• AI will attempt to resolve customer queries first</p>
                          <p>• After {maxUnsuccessfulResponses} failed attempts, human agents will be notified</p>
                          <p>• Customers can also request human help at any time</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-gray-900">85%</div>
                      <div className="text-sm text-gray-600">AI Resolution Rate</div>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-green-600">23</div>
                      <div className="text-sm text-gray-600">Daily Handoffs</div>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-blue-600">4.2m</div>
                      <div className="text-sm text-gray-600">Avg Response Time</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Security Tab */}
          {activeTab === "security" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Security Settings</h3>
                <p className="text-gray-600 mb-6">
                  Configure security policies and compliance settings.
                </p>

                <div className="space-y-4">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">PII Masking</h4>
                        <p className="text-sm text-gray-600">Automatically mask sensitive information in logs</p>
                      </div>
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          defaultChecked
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">Session Timeout</h4>
                      <p className="text-sm text-gray-600">Automatically log out inactive users</p>
                      <div className="mt-2">
                        <select className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                          <option>30 minutes</option>
                          <option>1 hour</option>
                          <option>2 hours</option>
                          <option>4 hours</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">IP Whitelist</h4>
                      <p className="text-sm text-gray-600">Restrict access to specific IP addresses</p>
                      <div className="mt-2">
                        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                          Configure IP Whitelist
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Save Button */}
          <div className="mt-8 pt-6 border-t border-gray-200 flex justify-end">
            <button
              onClick={handleSaveSettings}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
