"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  CheckCircle,
  AlertCircle,
  Smartphone,
  MessageSquare,
  Instagram,
  Settings,
  ArrowRight,
  Copy,
  ExternalLink
} from "lucide-react";

interface IntegrationStep {
  id: string;
  title: string;
  description: string;
  icon: any;
  completed: boolean;
  optional?: boolean;
}

export default function IntegrationSetup() {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [integrationData, setIntegrationData] = useState({
    whatsapp: { enabled: false, phoneNumber: "", apiToken: "" },
    facebook: { enabled: false, pageId: "", apiToken: "" },
    instagram: { enabled: false, accountId: "", apiToken: "" },
    crm: { enabled: false, apiUrl: "", apiKey: "", apiSecret: "" }
  });
  const router = useRouter();

  const steps: IntegrationStep[] = [
    {
      id: "welcome",
      title: "Welcome to BanglaChatPro",
      description: "Let's set up your AI agent for social media integration",
      icon: CheckCircle,
      completed: true
    },
    {
      id: "agent-setup",
      title: "Create Your AI Agent",
      description: "Configure your AI agent's personality and responses",
      icon: Settings,
      completed: false
    },
    {
      id: "whatsapp",
      title: "WhatsApp Integration",
      description: "Connect your WhatsApp Business account",
      icon: Smartphone,
      completed: false,
      optional: true
    },
    {
      id: "facebook",
      title: "Facebook Messenger",
      description: "Integrate with your Facebook Page",
      icon: MessageSquare,
      completed: false,
      optional: true
    },
    {
      id: "instagram",
      title: "Instagram Business",
      description: "Connect your Instagram Business account",
      icon: Instagram,
      completed: false,
      optional: true
    },
    {
      id: "crm",
      title: "CRM Integration (Optional)",
      description: "Connect to your existing CRM system",
      icon: Settings,
      completed: false,
      optional: true
    },
    {
      id: "test",
      title: "Test Your Integration",
      description: "Verify everything is working correctly",
      icon: CheckCircle,
      completed: false
    }
  ];

  const handleStepComplete = (stepId: string) => {
    if (!completedSteps.includes(stepId)) {
      setCompletedSteps([...completedSteps, stepId]);
    }
    setCurrentStep(currentStep + 1);
  };

  const handleIntegrationSave = async (platform: string, data: any) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        router.push("/login");
        return;
      }

      let endpoint = "";
      let payload = {};

      switch (platform) {
        case "whatsapp":
          endpoint = `/api/organizations/ai-agents/1/integrations/whatsapp`; // Replace 1 with actual agent ID
          payload = { phone_number: data.phoneNumber };
          break;
        case "facebook":
          endpoint = `/api/organizations/ai-agents/1/integrations/facebook`;
          payload = { page_id: data.pageId };
          break;
        case "instagram":
          endpoint = `/api/organizations/ai-agents/1/integrations/instagram`;
          payload = { account_id: data.accountId };
          break;
        case "crm":
          endpoint = `/api/organizations/integrations/crm`;
          payload = {
            api_url: data.apiUrl,
            api_key: data.apiKey,
            api_secret: data.apiSecret
          };
          break;
      }

      const response = await fetch(endpoint, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        setIntegrationData(prev => ({
          ...prev,
          [platform]: { ...prev[platform as keyof typeof prev], ...data, enabled: true }
        }));
        handleStepComplete(`${platform}`);
      } else {
        alert("Failed to save integration. Please try again.");
      }
    } catch (error) {
      console.error("Integration save failed:", error);
      alert("Failed to save integration. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🚀 AI Agent Integration Setup
          </h1>
          <p className="text-lg text-gray-600">
            Connect your AI agent to social media in just a few simple steps
          </p>
        </div>

        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  completedSteps.includes(step.id)
                    ? 'bg-green-500 text-white'
                    : currentStep === index
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}>
                  <step.icon className="w-5 h-5" />
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-16 h-1 mx-2 ${
                    completedSteps.includes(step.id) ? 'bg-green-500' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Step {currentStep + 1} of {steps.length}: {steps[currentStep]?.title}
            </p>
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          {currentStep === 0 && <WelcomeStep onComplete={() => handleStepComplete("welcome")} />}
          {currentStep === 1 && <AgentSetupStep onComplete={() => handleStepComplete("agent-setup")} />}
          {currentStep === 2 && <WhatsAppStep onSave={(data) => handleIntegrationSave("whatsapp", data)} />}
          {currentStep === 3 && <FacebookStep onSave={(data) => handleIntegrationSave("facebook", data)} />}
          {currentStep === 4 && <InstagramStep onSave={(data) => handleIntegrationSave("instagram", data)} />}
          {currentStep === 5 && <CRMSetupStep onSave={(data) => handleIntegrationSave("crm", data)} />}
          {currentStep === 6 && <TestIntegrationStep onComplete={() => handleStepComplete("test")} />}
        </div>

        {/* Navigation */}
        <div className="flex justify-between mt-8">
          <button
            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
            disabled={currentStep === 0}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          {currentStep < steps.length - 1 && (
            <button
              onClick={() => setCurrentStep(currentStep + 1)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Skip & Continue
              <ArrowRight className="w-4 h-4 ml-2 inline" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// Step Components
function WelcomeStep({ onComplete }: { onComplete: () => void }) {
  return (
    <div className="text-center">
      <div className="mb-6">
        <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome to BanglaChatPro!</h2>
        <p className="text-gray-600 mb-6">
          You're about to set up your AI agent to handle customer inquiries across multiple social media platforms.
          This process takes just 10-15 minutes and requires no technical knowledge.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <div className="text-center">
          <Smartphone className="w-12 h-12 text-green-500 mx-auto mb-2" />
          <h3 className="font-semibold mb-1">WhatsApp</h3>
          <p className="text-sm text-gray-600">Direct messaging integration</p>
        </div>
        <div className="text-center">
          <MessageSquare className="w-12 h-12 text-blue-500 mx-auto mb-2" />
          <h3 className="font-semibold mb-1">Facebook</h3>
          <p className="text-sm text-gray-600">Page messenger integration</p>
        </div>
        <div className="text-center">
          <Instagram className="w-12 h-12 text-pink-500 mx-auto mb-2" />
          <h3 className="font-semibold mb-1">Instagram</h3>
          <p className="text-sm text-gray-600">Business messaging</p>
        </div>
      </div>

      <button
        onClick={onComplete}
        className="px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700"
      >
        Let's Get Started!
        <ArrowRight className="w-5 h-5 ml-2 inline" />
      </button>
    </div>
  );
}

function AgentSetupStep({ onComplete }: { onComplete: () => void }) {
  const [agentData, setAgentData] = useState({
    name: "",
    description: "",
    personality: ""
  });

  const handleSave = async () => {
    // Here you would call the API to create/update the AI agent
    onComplete();
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Your AI Agent</h2>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Agent Name
          </label>
          <input
            type="text"
            value={agentData.name}
            onChange={(e) => setAgentData(prev => ({ ...prev, name: e.target.value }))}
            placeholder="e.g., Customer Support Assistant"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <textarea
            value={agentData.description}
            onChange={(e) => setAgentData(prev => ({ ...prev, description: e.target.value }))}
            placeholder="Describe what your AI agent will help customers with..."
            rows={3}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Personality & Tone
          </label>
          <select
            value={agentData.personality}
            onChange={(e) => setAgentData(prev => ({ ...prev, personality: e.target.value }))}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select personality...</option>
            <option value="professional">Professional & Formal</option>
            <option value="friendly">Friendly & Casual</option>
            <option value="helpful">Helpful & Supportive</option>
            <option value="expert">Expert & Knowledgeable</option>
          </select>
        </div>
      </div>

      <div className="mt-8 flex justify-end">
        <button
          onClick={handleSave}
          className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700"
        >
          Create Agent
        </button>
      </div>
    </div>
  );
}

function WhatsAppStep({ onSave }: { onSave: (data: any) => void }) {
  const [formData, setFormData] = useState({
    phoneNumber: "",
    apiToken: ""
  });

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">WhatsApp Integration</h2>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-start">
          <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-blue-900 mb-1">WhatsApp Business API Required</h3>
            <p className="text-blue-800 text-sm">
              To integrate WhatsApp, you need a WhatsApp Business API account.
              Don't worry - we'll guide you through the process!
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            WhatsApp Business Phone Number
          </label>
          <input
            type="tel"
            value={formData.phoneNumber}
            onChange={(e) => setFormData(prev => ({ ...prev, phoneNumber: e.target.value }))}
            placeholder="+880 1XX XXX XXXX"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            WhatsApp API Token
          </label>
          <input
            type="password"
            value={formData.apiToken}
            onChange={(e) => setFormData(prev => ({ ...prev, apiToken: e.target.value }))}
            placeholder="Your WhatsApp API token"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">Need Help Getting Started?</h3>
          <p className="text-gray-600 text-sm mb-3">
            Follow these simple steps to get your WhatsApp Business API:
          </p>
          <ol className="list-decimal list-inside text-sm text-gray-600 space-y-1">
            <li>Go to <a href="https://developers.facebook.com/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Facebook Developers</a></li>
            <li>Create a Business App</li>
            <li>Add WhatsApp product</li>
            <li>Get your phone number and API token</li>
          </ol>
        </div>
      </div>

      <div className="mt-8 flex justify-between">
        <button className="px-6 py-3 text-gray-600 hover:text-gray-800">
          Skip for Now
        </button>
        <button
          onClick={() => onSave(formData)}
          disabled={!formData.phoneNumber || !formData.apiToken}
          className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Connect WhatsApp
        </button>
      </div>
    </div>
  );
}

function FacebookStep({ onSave }: { onSave: (data: any) => void }) {
  const [formData, setFormData] = useState({
    pageId: "",
    apiToken: ""
  });

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Facebook Messenger Integration</h2>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Facebook Page ID
          </label>
          <input
            type="text"
            value={formData.pageId}
            onChange={(e) => setFormData(prev => ({ ...prev, pageId: e.target.value }))}
            placeholder="Your Facebook Page ID"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Facebook Access Token
          </label>
          <input
            type="password"
            value={formData.apiToken}
            onChange={(e) => setFormData(prev => ({ ...prev, apiToken: e.target.value }))}
            placeholder="Your Facebook Page Access Token"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">How to Get Facebook Access Token:</h3>
          <ol className="list-decimal list-inside text-sm text-gray-600 space-y-1">
            <li>Go to your Facebook Page</li>
            <li>Click "Settings" → "Messenger" → "Access Tokens"</li>
            <li>Generate a new token</li>
            <li>Copy the Page ID from the URL or settings</li>
          </ol>
        </div>
      </div>

      <div className="mt-8 flex justify-between">
        <button className="px-6 py-3 text-gray-600 hover:text-gray-800">
          Skip for Now
        </button>
        <button
          onClick={() => onSave(formData)}
          disabled={!formData.pageId || !formData.apiToken}
          className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Connect Facebook
        </button>
      </div>
    </div>
  );
}

function InstagramStep({ onSave }: { onSave: (data: any) => void }) {
  const [formData, setFormData] = useState({
    accountId: "",
    apiToken: ""
  });

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Instagram Business Integration</h2>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Instagram Account ID
          </label>
          <input
            type="text"
            value={formData.accountId}
            onChange={(e) => setFormData(prev => ({ ...prev, accountId: e.target.value }))}
            placeholder="Your Instagram Business Account ID"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">Instagram uses Facebook's API:</h3>
          <p className="text-gray-600 text-sm">
            Instagram Business messaging uses the same access token as Facebook.
            If you connected Facebook above, you can use the same token here.
          </p>
        </div>
      </div>

      <div className="mt-8 flex justify-between">
        <button className="px-6 py-3 text-gray-600 hover:text-gray-800">
          Skip for Now
        </button>
        <button
          onClick={() => onSave(formData)}
          disabled={!formData.accountId}
          className="px-6 py-3 bg-pink-600 text-white font-semibold rounded-lg hover:bg-pink-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Connect Instagram
        </button>
      </div>
    </div>
  );
}

function CRMSetupStep({ onSave }: { onSave: (data: any) => void }) {
  const [formData, setFormData] = useState({
    apiUrl: "",
    apiKey: "",
    apiSecret: ""
  });

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">CRM Integration (Optional)</h2>
      <p className="text-gray-600 mb-6">
        Connect your existing CRM system to provide real-time customer data to your AI agent.
      </p>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            CRM API URL
          </label>
          <input
            type="url"
            value={formData.apiUrl}
            onChange={(e) => setFormData(prev => ({ ...prev, apiUrl: e.target.value }))}
            placeholder="https://your-crm-api.com/api"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            API Key
          </label>
          <input
            type="password"
            value={formData.apiKey}
            onChange={(e) => setFormData(prev => ({ ...prev, apiKey: e.target.value }))}
            placeholder="Your CRM API key"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            API Secret (Optional)
          </label>
          <input
            type="password"
            value={formData.apiSecret}
            onChange={(e) => setFormData(prev => ({ ...prev, apiSecret: e.target.value }))}
            placeholder="Your CRM API secret"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-yellow-900 mb-1">Supported CRM Systems</h3>
              <p className="text-yellow-800 text-sm">
                Our system works with most REST API-based CRM systems including Salesforce, HubSpot, Zoho CRM, and custom APIs.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 flex justify-between">
        <button className="px-6 py-3 text-gray-600 hover:text-gray-800">
          Skip CRM Integration
        </button>
        <button
          onClick={() => onSave(formData)}
          disabled={!formData.apiUrl || !formData.apiKey}
          className="px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Connect CRM
        </button>
      </div>
    </div>
  );
}

function TestIntegrationStep({ onComplete }: { onComplete: () => void }) {
  const [testResults, setTestResults] = useState({
    whatsapp: null,
    facebook: null,
    instagram: null,
    crm: null
  });

  const runTests = async () => {
    // Here you would test each integration
    // For now, just mark as completed
    onComplete();
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Test Your Integrations</h2>
      <p className="text-gray-600 mb-6">
        Let's verify that all your integrations are working correctly.
      </p>

      <div className="space-y-4">
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Smartphone className="w-6 h-6 text-green-500 mr-3" />
              <span className="font-medium">WhatsApp Integration</span>
            </div>
            <span className="text-sm text-gray-500">Ready to test</span>
          </div>
        </div>

        <div className="border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <MessageSquare className="w-6 h-6 text-blue-500 mr-3" />
              <span className="font-medium">Facebook Integration</span>
            </div>
            <span className="text-sm text-gray-500">Ready to test</span>
          </div>
        </div>

        <div className="border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Instagram className="w-6 h-6 text-pink-500 mr-3" />
              <span className="font-medium">Instagram Integration</span>
            </div>
            <span className="text-sm text-gray-500">Ready to test</span>
          </div>
        </div>
      </div>

      <div className="mt-8 text-center">
        <button
          onClick={runTests}
          className="px-8 py-4 bg-green-600 text-white text-lg font-semibold rounded-lg hover:bg-green-700"
        >
          Complete Setup
          <CheckCircle className="w-5 h-5 ml-2 inline" />
        </button>
        <p className="text-sm text-gray-600 mt-3">
          Your AI agent is now ready to handle customer inquiries!
        </p>
      </div>
    </div>
  );
}
