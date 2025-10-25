import { MessageSquare, Mic, Brain, Zap, Shield, Users, Smartphone, Facebook, Instagram, Phone, Bot, BarChart3 } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI Agent Training",
    description: "Upload your documents, knowledge base, and training data to create custom AI agents that understand your business perfectly.",
    color: "from-blue-500 to-cyan-500"
  },
  {
    icon: MessageSquare,
    title: "Multi-Platform Chat",
    description: "Deploy your AI agents across web chat, WhatsApp, Facebook Messenger, and Instagram with unified conversation management.",
    color: "from-green-500 to-emerald-500"
  },
  {
    icon: Phone,
    title: "Voice Call Support (IVR)",
    description: "Handle phone calls with intelligent voice responses, automatic language detection, and seamless human handoff when needed.",
    color: "from-purple-500 to-pink-500"
  },
  {
    icon: Bot,
    title: "Smart Escalation",
    description: "AI automatically escalates complex queries to human agents after analyzing confidence scores and user satisfaction.",
    color: "from-orange-500 to-red-500"
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    description: "Bank-level encryption, PII masking, GDPR compliance, and secure API integrations protect your customer data.",
    color: "from-gray-700 to-gray-900"
  },
  {
    icon: BarChart3,
    title: "Advanced Analytics",
    description: "Comprehensive dashboards showing conversation metrics, user satisfaction, response times, and platform performance.",
    color: "from-indigo-500 to-purple-500"
  }
];

const integrations = [
  { name: "WhatsApp Business", icon: "💬", description: "Automated customer support via WhatsApp" },
  { name: "Facebook Messenger", icon: "📘", description: "Seamless Facebook page integration" },
  { name: "Instagram Business", icon: "📷", description: "Instagram DM automation" },
  { name: "Web Chat Widget", icon: "🌐", description: "Embedded chat for your website" },
  { name: "Voice Calls (IVR)", icon: "📞", description: "Intelligent phone call handling" },
  { name: "CRM Integration", icon: "🔗", description: "Connect with your existing systems" }
];

export default function FeaturesSection() {
  return (
    <section id="features" className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-7xl mx-auto">
        {/* Main Features */}
        <div className="text-center mb-20">
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Complete AI Customer Service
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 block">
              Platform
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            From training your AI agents to deploying them across all your customer touchpoints,
            we provide everything you need for exceptional customer service automation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-20">
          {features.map((feature, index) => (
            <div key={index} className="group relative bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100">
              <div className={`w-16 h-16 bg-gradient-to-r ${feature.color} rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                <feature.icon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">{feature.title}</h3>
              <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              <div className={`absolute bottom-0 left-0 h-1 bg-gradient-to-r ${feature.color} rounded-b-2xl transition-all duration-300 group-hover:h-2`}></div>
            </div>
          ))}
        </div>

        {/* Integration Showcase */}
        <div className="bg-gradient-to-r from-slate-900 to-gray-900 rounded-3xl p-12 text-white mb-20">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold mb-4">Seamless Platform Integration</h3>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Connect your AI agents with all the platforms your customers use
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {integrations.map((integration, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300">
                <div className="text-4xl mb-4">{integration.icon}</div>
                <h4 className="text-lg font-semibold mb-2">{integration.name}</h4>
                <p className="text-gray-300 text-sm">{integration.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-3xl shadow-2xl p-12 mb-20">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">How It Works</h3>
            <p className="text-lg text-gray-600">Get started in minutes, not months</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                <span className="text-2xl font-bold text-white">1</span>
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">Train Your AI Agent</h4>
              <p className="text-gray-600">Upload your documents, FAQs, and knowledge base. Our AI learns your business context and communication style.</p>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                <span className="text-2xl font-bold text-white">2</span>
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">Configure Integrations</h4>
              <p className="text-gray-600">Connect WhatsApp, Facebook, Instagram, and other platforms. Set up voice call routing and CRM integrations.</p>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-r from-pink-500 to-red-500 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                <span className="text-2xl font-bold text-white">3</span>
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">Go Live & Monitor</h4>
              <p className="text-gray-600">Deploy your AI agents and monitor performance with real-time analytics. Human oversight ensures quality.</p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl p-12 text-white">
          <h3 className="text-3xl font-bold mb-4">
            Ready to Transform Your Customer Service?
          </h3>
          <p className="text-xl mb-8 max-w-2xl mx-auto opacity-90">
            Join thousands of businesses using AI to deliver exceptional customer experiences.
            Start your free trial today and see the difference intelligent automation makes.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/register"
              className="bg-white text-blue-600 px-8 py-4 rounded-xl font-bold text-lg hover:bg-gray-100 transition-colors shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              Start Free Trial
            </a>
            <a
              href="/dashboard"
              className="bg-white/20 backdrop-blur-sm text-white border border-white/30 px-8 py-4 rounded-xl font-bold text-lg hover:bg-white/30 transition-colors"
            >
              View Dashboard Demo
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
