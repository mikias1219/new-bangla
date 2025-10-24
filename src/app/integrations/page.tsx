import Link from "next/link";
import Navigation from "@/components/Navigation";

const integrations = [
  {
    name: "WhatsApp Business",
    description: "Connect with customers on the world's most popular messaging platform",
    features: ["Automated responses", "24/7 availability", "Rich media support", "Business verification"],
    icon: "💬",
    status: "Available",
    category: "Messaging"
  },
  {
    name: "Facebook Messenger",
    description: "Integrate AI chat into your Facebook business page conversations",
    features: ["Page integration", "Messenger plugins", "Automated handoffs", "Analytics"],
    icon: "📘",
    status: "Available",
    category: "Social Media"
  },
  {
    name: "Instagram",
    description: "Handle Instagram direct messages with intelligent AI responses",
    features: ["DM automation", "Story responses", "Comment management", "Brand consistency"],
    icon: "📷",
    status: "Available",
    category: "Social Media"
  },
  {
    name: "Telegram",
    description: "Power your Telegram bots with advanced AI conversation capabilities",
    features: ["Bot integration", "Channel management", "Group chat support", "Inline queries"],
    icon: "✈️",
    status: "Coming Soon",
    category: "Messaging"
  },
  {
    name: "Slack",
    description: "Add AI assistance to your Slack workspace for enhanced productivity",
    features: ["Workspace integration", "Channel bots", "Direct messages", "Slash commands"],
    icon: "💼",
    status: "Coming Soon",
    category: "Productivity"
  },
  {
    name: "Discord",
    description: "Engage your community with AI-powered Discord bots and automation",
    features: ["Server bots", "Voice integration", "Role management", "Moderation"],
    icon: "🎮",
    status: "Coming Soon",
    category: "Community"
  },
  {
    name: "Website Chat Widget",
    description: "Embed live chat on your website with customizable AI responses",
    features: ["Customizable design", "Real-time responses", "Lead capture", "Analytics"],
    icon: "🌐",
    status: "Available",
    category: "Web"
  },
  {
    name: "WordPress",
    description: "Seamlessly integrate AI chat into your WordPress website",
    features: ["Plugin integration", "Shortcode support", "Theme compatibility", "SEO friendly"],
    icon: "📝",
    status: "Available",
    category: "CMS"
  },
  {
    name: "Shopify",
    description: "Enhance your e-commerce store with AI-powered customer support",
    features: ["Order assistance", "Product recommendations", "Cart recovery", "24/7 support"],
    icon: "🛒",
    status: "Available",
    category: "E-commerce"
  },
  {
    name: "Zapier",
    description: "Connect Bangla Chat Pro with thousands of apps through Zapier",
    features: ["Workflow automation", "Data synchronization", "Event triggers", "Custom actions"],
    icon: "🔗",
    status: "Available",
    category: "Automation"
  },
  {
    name: "API Integration",
    description: "Build custom integrations with our comprehensive REST API",
    features: ["Full API access", "Webhook support", "Custom endpoints", "Rate limiting"],
    icon: "⚙️",
    status: "Available",
    category: "Developer"
  },
  {
    name: "CRM Systems",
    description: "Sync conversations and customer data with popular CRM platforms",
    features: ["Contact synchronization", "Lead management", "Ticket creation", "Reporting"],
    icon: "📊",
    status: "Coming Soon",
    category: "Business"
  }
];

const categories = ["All", "Messaging", "Social Media", "Productivity", "Community", "Web", "CMS", "E-commerce", "Automation", "Developer", "Business"];

export default function IntegrationsPage() {
  return (
    <div className="min-h-screen bg-white">
      <Navigation />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Integrations
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Connect Bangla Chat Pro with your favorite tools and platforms. Streamline your workflow and extend AI capabilities across your entire tech stack.
          </p>
        </div>

        {/* Integration Stats */}
        <div className="bg-blue-50 rounded-xl p-8 mb-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">50+</div>
              <div className="text-gray-600">Available Integrations</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">24/7</div>
              <div className="text-gray-600">Automated Support</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">99.9%</div>
              <div className="text-gray-600">Uptime Guarantee</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">5min</div>
              <div className="text-gray-600">Average Setup Time</div>
            </div>
          </div>
        </div>

        {/* Category Filter */}
        <div className="mb-12">
          <div className="flex flex-wrap justify-center gap-3">
            {categories.map((category) => (
              <button
                key={category}
                className="px-4 py-2 rounded-full border border-gray-300 text-gray-700 hover:border-blue-500 hover:text-blue-600 transition-colors"
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* Integration Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {integrations.map((integration, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="text-4xl mb-3">{integration.icon}</div>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                  integration.status === 'Available' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {integration.status}
                </span>
              </div>

              <h3 className="text-xl font-bold text-gray-900 mb-2">{integration.name}</h3>
              <p className="text-gray-600 mb-4">{integration.description}</p>

              <div className="mb-4">
                <span className="inline-block bg-blue-100 text-blue-800 text-sm font-semibold px-3 py-1 rounded-full">
                  {integration.category}
                </span>
              </div>

              <ul className="space-y-2 mb-6">
                {integration.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-center text-sm text-gray-600">
                    <svg className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>

              <button className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
                integration.status === 'Available'
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-100 text-gray-400 cursor-not-allowed'
              }`}>
                {integration.status === 'Available' ? 'Connect Now' : 'Coming Soon'}
              </button>
            </div>
          ))}
        </div>

        {/* Custom Integration */}
        <div className="bg-gray-50 rounded-xl p-8 mb-12">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Need a Custom Integration?</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Don&apos;t see your favorite platform? Our developer team can create custom integrations tailored to your specific needs and workflows.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">API Access</h3>
              <p className="text-gray-600 text-sm">Full REST API with comprehensive documentation</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Webhooks</h3>
              <p className="text-gray-600 text-sm">Real-time event notifications and data sync</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192L5.636 18.364M12 2.944l4.95 4.95M12 2.944L7.05 7.894M12 21.056l4.95-4.95M12 21.056l-4.95-4.95" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">SDKs</h3>
              <p className="text-gray-600 text-sm">Official libraries for popular programming languages</p>
            </div>
          </div>

          <div className="text-center mt-8">
            <Link
              href="/contact"
              className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Request Custom Integration
            </Link>
          </div>
        </div>

        {/* Setup Guide */}
        <div className="bg-white border border-gray-200 rounded-xl p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Quick Setup Guide</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">1. Choose Your Platform</h3>
              <p className="text-gray-600 mb-4">
                Select the platform you want to integrate with from our available options or request a custom integration.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">2. Configure Settings</h3>
              <p className="text-gray-600 mb-4">
                Follow our step-by-step setup guide to configure authentication and connection settings.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">3. Test Integration</h3>
              <p className="text-gray-600 mb-4">
                Use our testing tools to verify that your integration is working correctly and handling conversations properly.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">4. Go Live</h3>
              <p className="text-gray-600 mb-4">
                Deploy your integration and start providing AI-powered customer support across all your channels.
              </p>
            </div>
          </div>
        </div>

        {/* Support */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Need Help with Integration?</h2>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            Our integration specialists are here to help you set up and optimize your connections. Get expert assistance and best practices.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/help"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              View Documentation
            </Link>
            <Link
              href="/contact"
              className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Contact Support
            </Link>
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
