import Link from "next/link";
import Navigation from "@/components/Navigation";

const apiEndpoints = [
  {
    method: "POST",
    endpoint: "/api/v1/chat/send",
    description: "Send a message to the AI chat",
    parameters: [
      { name: "message", type: "string", required: true, description: "The message to send to the AI" },
      { name: "session_id", type: "string", required: false, description: "Session ID for conversation continuity" },
      { name: "agent_id", type: "string", required: false, description: "Specific AI agent to use" }
    ],
    example: `{
  "message": "Hello, how can you help me?",
  "session_id": "sess_12345",
  "agent_id": "agent_67890"
}`
  },
  {
    method: "GET",
    endpoint: "/api/v1/chat/history",
    description: "Get conversation history",
    parameters: [
      { name: "session_id", type: "string", required: true, description: "Session ID to retrieve history for" },
      { name: "limit", type: "number", required: false, description: "Maximum number of messages to return (default: 50)" }
    ],
    example: `{
  "session_id": "sess_12345",
  "limit": 20
}`
  },
  {
    method: "POST",
    endpoint: "/api/v1/agents",
    description: "Create a new AI agent",
    parameters: [
      { name: "name", type: "string", required: true, description: "Name of the AI agent" },
      { name: "description", type: "string", required: false, description: "Description of the agent's purpose" },
      { name: "prompt", type: "string", required: true, description: "System prompt for the agent" },
      { name: "model", type: "string", required: false, description: "AI model to use (default: gpt-4)" }
    ],
    example: `{
  "name": "Customer Support Agent",
  "description": "Handles customer inquiries",
  "prompt": "You are a helpful customer support agent...",
  "model": "gpt-4"
}`
  },
  {
    method: "GET",
    endpoint: "/api/v1/agents/{agent_id}",
    description: "Get agent details",
    parameters: [
      { name: "agent_id", type: "string", required: true, description: "ID of the agent to retrieve" }
    ],
    example: "GET /api/v1/agents/agent_67890"
  },
  {
    method: "POST",
    endpoint: "/api/v1/webhooks",
    description: "Create a webhook for events",
    parameters: [
      { name: "url", type: "string", required: true, description: "Webhook URL to receive events" },
      { name: "events", type: "array", required: true, description: "Array of events to listen for" },
      { name: "secret", type: "string", required: false, description: "Webhook secret for verification" }
    ],
    example: `{
  "url": "https://your-app.com/webhook",
  "events": ["message.received", "conversation.ended"],
  "secret": "your_webhook_secret"
}`
  }
];

const codeExamples = {
  javascript: `// Send a message
const response = await fetch('/api/v1/chat/send', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_API_KEY'
  },
  body: JSON.stringify({
    message: "Hello, how can you help me?",
    session_id: "sess_12345"
  })
});

const data = await response.json();
console.log(data.response);`,
  python: `# Send a message
import requests

url = "/api/v1/chat/send"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY"
}
data = {
    "message": "Hello, how can you help me?",
    "session_id": "sess_12345"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()
print(result['response'])`,
  curl: `curl -X POST "/api/v1/chat/send" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -d '{
    "message": "Hello, how can you help me?",
    "session_id": "sess_12345"
  }'`
};

export default function ApiDocsPage() {
  return (
    <div className="min-h-screen bg-white">
      <Navigation />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            API Documentation
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Integrate Bangla Chat Pro into your applications with our comprehensive API. Build custom chat experiences and automate conversations.
          </p>
        </div>

        {/* Quick Start */}
        <div className="bg-blue-50 rounded-xl p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick Start</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-blue-600 font-bold">1</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Get API Key</h3>
              <p className="text-gray-600 text-sm">Sign up and generate your API key from the dashboard</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-blue-600 font-bold">2</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Make Request</h3>
              <p className="text-gray-600 text-sm">Use our REST API to send messages and manage conversations</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-blue-600 font-bold">3</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Integrate</h3>
              <p className="text-gray-600 text-sm">Build your application with real-time chat capabilities</p>
            </div>
          </div>
        </div>

        {/* Authentication */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Authentication</h2>
          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Bearer Token</h3>
            <p className="text-gray-600 mb-4">
              Include your API key in the Authorization header as a Bearer token for all API requests.
            </p>
            <div className="bg-gray-800 text-gray-100 p-4 rounded-lg font-mono text-sm">
              Authorization: Bearer YOUR_API_KEY
            </div>
          </div>
        </div>

        {/* API Endpoints */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">API Endpoints</h2>
          <div className="space-y-8">
            {apiEndpoints.map((endpoint, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-center gap-3 mb-4">
                  <span className={`px-3 py-1 rounded text-sm font-semibold ${
                    endpoint.method === 'GET' ? 'bg-green-100 text-green-800' :
                    endpoint.method === 'POST' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {endpoint.method}
                  </span>
                  <code className="text-lg font-mono text-gray-900">{endpoint.endpoint}</code>
                </div>
                <p className="text-gray-600 mb-4">{endpoint.description}</p>

                {endpoint.parameters.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-semibold text-gray-900 mb-2">Parameters</h4>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-gray-200">
                            <th className="text-left py-2 font-semibold">Name</th>
                            <th className="text-left py-2 font-semibold">Type</th>
                            <th className="text-left py-2 font-semibold">Required</th>
                            <th className="text-left py-2 font-semibold">Description</th>
                          </tr>
                        </thead>
                        <tbody>
                          {endpoint.parameters.map((param, paramIndex) => (
                            <tr key={paramIndex} className="border-b border-gray-100">
                              <td className="py-2 font-mono text-blue-600">{param.name}</td>
                              <td className="py-2 text-gray-600">{param.type}</td>
                              <td className="py-2">
                                <span className={`px-2 py-1 rounded text-xs ${
                                  param.required ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                                }`}>
                                  {param.required ? 'Yes' : 'No'}
                                </span>
                              </td>
                              <td className="py-2 text-gray-600">{param.description}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Example Request</h4>
                  <pre className="bg-gray-800 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                    <code>{endpoint.example}</code>
                  </pre>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Code Examples */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Code Examples</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">JavaScript</h3>
              <pre className="bg-gray-800 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                <code>{codeExamples.javascript}</code>
              </pre>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Python</h3>
              <pre className="bg-gray-800 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                <code>{codeExamples.python}</code>
              </pre>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">cURL</h3>
              <pre className="bg-gray-800 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                <code>{codeExamples.curl}</code>
              </pre>
            </div>
          </div>
        </div>

        {/* SDKs */}
        <div className="bg-gray-50 rounded-xl p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">SDKs & Libraries</h2>
          <p className="text-gray-600 mb-6">
            Speed up your integration with our official SDKs and community libraries.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">JavaScript SDK</h3>
              <p className="text-gray-600 text-sm mb-4">Official SDK for Node.js and browsers</p>
              <a href="#" className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                View on GitHub →
              </a>
            </div>
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">Python SDK</h3>
              <p className="text-gray-600 text-sm mb-4">Official SDK for Python applications</p>
              <a href="#" className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                View on GitHub →
              </a>
            </div>
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">PHP SDK</h3>
              <p className="text-gray-600 text-sm mb-4">Community-maintained PHP library</p>
              <a href="#" className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                View on GitHub →
              </a>
            </div>
          </div>
        </div>

        {/* Rate Limits */}
        <div className="bg-yellow-50 rounded-xl p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Rate Limits</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-600 mb-2">1000</div>
              <div className="text-gray-600">Requests per minute</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-600 mb-2">10000</div>
              <div className="text-gray-600">Requests per hour</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-600 mb-2">50000</div>
              <div className="text-gray-600">Requests per day</div>
            </div>
          </div>
          <p className="text-gray-600 mt-4">
            Rate limits vary by your subscription plan. Contact us for enterprise limits.
          </p>
        </div>

        {/* Support */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Need Help?</h2>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            Can&apos;t find what you&apos;re looking for? Our developer community and support team are here to help.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/contact"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Contact Support
            </Link>
            <a
              href="https://github.com/banglachatpro"
              className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              View GitHub
            </a>
          </div>
        </div>

        <div className="text-center mt-12">
          <Link
            href="/"
            className="inline-block bg-gray-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
          >
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
