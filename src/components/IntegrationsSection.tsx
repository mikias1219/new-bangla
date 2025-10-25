import { Smartphone, MessageSquare, Facebook, Instagram, Phone, Database, Zap, CheckCircle } from "lucide-react";

const integrations = [
  {
    name: "WhatsApp Business API",
    icon: MessageSquare,
    description: "Connect your WhatsApp Business account for automated customer support",
    features: ["Auto-responses", "24/7 availability", "Rich media support"],
    color: "from-green-500 to-emerald-500",
    status: "ready"
  },
  {
    name: "Facebook Messenger",
    icon: Facebook,
    description: "Handle Facebook page messages and customer inquiries automatically",
    features: ["Page integration", "Quick replies", "User management"],
    color: "from-blue-500 to-blue-600",
    status: "ready"
  },
  {
    name: "Instagram Business",
    icon: Instagram,
    description: "Manage Instagram DMs and brand engagement with AI responses",
    features: ["DM automation", "Story responses", "Brand consistency"],
    color: "from-pink-500 to-purple-500",
    status: "ready"
  },
  {
    name: "Voice Calls (IVR)",
    icon: Phone,
    description: "Intelligent phone call handling with natural Bangla voice responses",
    features: ["Bangla TTS", "Auto-attendant", "Call routing"],
    color: "from-purple-500 to-indigo-500",
    status: "ready"
  },
  {
    name: "Web Chat Widget",
    icon: Smartphone,
    description: "Embed AI chat on your website for instant customer support",
    features: ["Easy integration", "Customizable UI", "Real-time responses"],
    color: "from-blue-500 to-cyan-500",
    status: "ready"
  },
  {
    name: "CRM Integration",
    icon: Database,
    description: "Connect with your existing CRM and ERP systems for data-driven responses",
    features: ["Order lookup", "Customer data", "Inventory sync"],
    color: "from-gray-600 to-gray-800",
    status: "ready"
  }
];

export default function IntegrationsSection() {
  return (
    <section id="integrations" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-blue-50 px-4 py-2 rounded-full mb-6">
            <Zap className="w-4 h-4 text-blue-600" />
            <span className="text-blue-700 text-sm font-medium">Platform Integrations</span>
          </div>
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            Connect Everywhere Your Customers Are
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Seamlessly integrate your AI agents across all major communication platforms.
            One AI agent, multiple touchpoints, unified customer experience.
          </p>
        </div>

        {/* Integration Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {integrations.map((integration, index) => (
            <div
              key={index}
              className="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 bg-gradient-to-r ${integration.color} rounded-xl flex items-center justify-center`}>
                  <integration.icon className="w-6 h-6 text-white" />
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span className="text-xs text-green-700 font-medium">Ready</span>
                </div>
              </div>

              {/* Content */}
              <h3 className="text-lg font-bold text-gray-900 mb-2">{integration.name}</h3>
              <p className="text-gray-600 mb-4 leading-relaxed">{integration.description}</p>

              {/* Features */}
              <div className="space-y-2">
                {integration.features.map((feature, featureIndex) => (
                  <div key={featureIndex} className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                    <span className="text-sm text-gray-700">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Integration Process */}
        <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-3xl p-8 md:p-12 text-white">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold mb-4">How Integration Works</h3>
            <p className="text-gray-300 text-lg">Get started in under 5 minutes</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center group">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <span className="text-2xl font-bold">1</span>
              </div>
              <h4 className="text-xl font-bold mb-3">Connect</h4>
              <p className="text-gray-300 leading-relaxed">
                Link your business accounts using secure API keys and webhooks.
                We handle the technical setup for you.
              </p>
            </div>

            <div className="text-center group">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <span className="text-2xl font-bold">2</span>
              </div>
              <h4 className="text-xl font-bold mb-3">Configure</h4>
              <p className="text-gray-300 leading-relaxed">
                Choose which AI agent handles messages from each platform.
                Set custom greetings and response rules.
              </p>
            </div>

            <div className="text-center group">
              <div className="w-16 h-16 bg-gradient-to-r from-pink-500 to-red-500 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <span className="text-2xl font-bold">3</span>
              </div>
              <h4 className="text-xl font-bold mb-3">Go Live</h4>
              <p className="text-gray-300 leading-relaxed">
                Your AI agents start responding instantly. Monitor performance
                and optimize responses in real-time.
              </p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center mt-16">
          <div className="bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl p-8 text-white shadow-2xl">
            <h3 className="text-2xl font-bold mb-4">Ready to Connect Your Platforms?</h3>
            <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
              Start your free trial and connect your first platform in minutes.
              No complex setup required.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/register"
                className="bg-white text-blue-600 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition-colors shadow-lg"
              >
                Start Free Trial
              </a>
              <a
                href="/dashboard"
                className="bg-white/20 backdrop-blur-sm text-white border border-white/30 px-8 py-3 rounded-lg font-bold hover:bg-white/30 transition-colors"
              >
                View Dashboard Demo
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
