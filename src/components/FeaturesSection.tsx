import { MessageSquare, Mic, Brain, Zap, Shield, Users } from "lucide-react";

const features = [
  {
    icon: MessageSquare,
    title: "Intelligent Conversations",
    description: "Engage in natural, context-aware conversations with our advanced AI that understands and responds like a human expert."
  },
  {
    icon: Mic,
    title: "Voice Messages",
    description: "Send and receive voice messages. Our AI can transcribe speech and respond with natural voice synthesis."
  },
  {
    icon: Brain,
    title: "Personalized AI Models",
    description: "Train custom AI models tailored to your specific needs, industry, or communication style."
  },
  {
    icon: Zap,
    title: "Lightning Fast Responses",
    description: "Get instant responses powered by cutting-edge AI technology with minimal latency."
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    description: "Bank-level encryption and privacy protection ensure your conversations remain completely secure."
  },
  {
    icon: Users,
    title: "Multi-language Support",
    description: "Communicate seamlessly in multiple languages including Bangla, English, and many more."
  }
];

export default function FeaturesSection() {
  return (
    <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            What Makes Bangla Chat Pro Different?
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            We help you communicate more effectively, solve problems faster, and achieve your goals
            with AI-powered conversations that feel natural and productive.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-gray-50 p-8 rounded-xl hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <feature.icon className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>

        <div className="text-center mt-16">
          <div className="bg-blue-50 p-8 rounded-2xl">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Ready to Transform Your Communication?
            </h3>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Join thousands of users who have already discovered the power of AI-driven conversations.
              Start your free trial today and experience the difference.
            </p>
            <a
              href="/register"
              className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Start Your Free Trial
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
