import { Clock, Sparkles, Zap, Globe, Shield, Users } from "lucide-react";

const roadmapItems = [
  {
    title: "Advanced Voice Synthesis",
    description: "Enhanced voice capabilities with emotion detection and natural conversation flow.",
    icon: Sparkles,
    timeline: "Q2 2025",
    status: "in-development"
  },
  {
    title: "Multi-Modal AI",
    description: "Support for images, documents, and complex data analysis in conversations.",
    icon: Zap,
    timeline: "Q3 2025",
    status: "planned"
  },
  {
    title: "Global Language Expansion",
    description: "Adding support for 50+ languages including regional dialects and accents.",
    icon: Globe,
    timeline: "Q4 2025",
    status: "planned"
  },
  {
    title: "Enterprise API Suite",
    description: "Complete API ecosystem for seamless integration with business systems.",
    icon: Shield,
    timeline: "Q1 2026",
    status: "planned"
  },
  {
    title: "Collaborative Workspaces",
    description: "Team collaboration features with shared AI models and conversation history.",
    icon: Users,
    timeline: "Q2 2026",
    status: "planned"
  },
  {
    title: "AI Agent Marketplace",
    description: "Platform for custom AI agents created by users and shared with the community.",
    icon: Clock,
    timeline: "Q3 2026",
    status: "vision"
  }
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "in-development":
      return "bg-blue-100 text-blue-800 border-blue-200";
    case "planned":
      return "bg-green-100 text-green-800 border-green-200";
    case "vision":
      return "bg-purple-100 text-purple-800 border-purple-200";
    default:
      return "bg-gray-100 text-gray-800 border-gray-200";
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case "in-development":
      return "In Development";
    case "planned":
      return "Planned";
    case "vision":
      return "Vision";
    default:
      return "Coming Soon";
  }
};

export default function RoadmapSection() {
  return (
    <section id="roadmap" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-50 to-indigo-50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            What's Coming Next
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            We're continuously innovating to bring you the most advanced AI conversation experience.
            Here's our roadmap for the future.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {roadmapItems.map((item, index) => (
            <div key={index} className="bg-white rounded-xl p-6 shadow-sm hover:shadow-lg transition-shadow border border-gray-100">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <item.icon className="w-6 h-6 text-blue-600" />
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(item.status)}`}>
                  {getStatusText(item.status)}
                </span>
              </div>

              <h3 className="text-xl font-semibold text-gray-900 mb-3">{item.title}</h3>
              <p className="text-gray-600 mb-4 leading-relaxed">{item.description}</p>

              <div className="flex items-center text-sm text-gray-500">
                <Clock className="w-4 h-4 mr-2" />
                <span>{item.timeline}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center mt-16">
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Have a Feature Request?
            </h3>
            <p className="text-gray-600 mb-6">
              We're always listening to our users. Share your ideas and help shape the future of AI conversations.
            </p>
            <a
              href="/feedback"
              className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Share Your Ideas
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
