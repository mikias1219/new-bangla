import Link from "next/link";
import Navigation from "@/components/Navigation";

const faqData = [
  {
    question: "How do I get started with Bangla Chat Pro?",
    answer: "Getting started is easy! Simply sign up for a free trial, choose your plan, and start chatting with our AI immediately. Our onboarding process will guide you through setup and integration."
  },
  {
    question: "What languages does Bangla Chat Pro support?",
    answer: "We support multiple languages including English, Bangla, Hindi, and many others. Our AI can understand and respond in the language you communicate in."
  },
  {
    question: "How secure is my data?",
    answer: "Security is our top priority. We use end-to-end encryption, comply with GDPR standards, and never store your conversations without explicit consent. All data is processed securely in compliance with international privacy standards."
  },
  {
    question: "Can I integrate Bangla Chat Pro with other platforms?",
    answer: "Yes! We offer integrations with popular platforms including WhatsApp, Facebook Messenger, Instagram, and custom API integrations. Check our integrations page for more details."
  },
  {
    question: "What are the pricing plans?",
    answer: "We offer flexible pricing starting with a free tier, then Basic ($29/month), Pro ($79/month), and Enterprise (custom pricing). Each plan includes different features and usage limits."
  },
  {
    question: "How do I customize the AI responses?",
    answer: "You can customize AI responses through our admin dashboard. Set up custom prompts, define conversation flows, and train the AI on your specific domain knowledge."
  },
  {
    question: "Is there a limit on conversations?",
    answer: "Conversation limits vary by plan. Free tier includes 100 conversations/month, Basic includes 1,000, Pro includes 10,000, and Enterprise has unlimited conversations."
  },
  {
    question: "How do I contact support?",
    answer: "You can reach our support team through the contact form, email us at support@banglachatpro.com, or use the live chat feature in your dashboard."
  }
];

const helpCategories = [
  {
    title: "Getting Started",
    items: [
      "Account Setup Guide",
      "First Conversation Tutorial",
      "Dashboard Overview",
      "Basic Configuration"
    ]
  },
  {
    title: "AI Customization",
    items: [
      "Custom Prompts",
      "Training Your AI",
      "Personality Settings",
      "Response Templates"
    ]
  },
  {
    title: "Integrations",
    items: [
      "WhatsApp Integration",
      "Facebook Messenger Setup",
      "Instagram Integration",
      "API Documentation"
    ]
  },
  {
    title: "Billing & Account",
    items: [
      "Subscription Management",
      "Payment Methods",
      "Usage Analytics",
      "Account Settings"
    ]
  }
];

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-white">
      <Navigation />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Help Center
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Find answers to common questions and get the help you need to make the most of Bangla Chat Pro.
          </p>
        </div>

        {/* Search Bar */}
        <div className="max-w-2xl mx-auto mb-12">
          <div className="relative">
            <input
              type="text"
              placeholder="Search for help..."
              className="w-full px-6 py-4 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button className="absolute right-3 top-3 bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
          </div>
        </div>

        {/* Help Categories */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {helpCategories.map((category, index) => (
            <div key={index} className="bg-gray-50 rounded-xl p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">{category.title}</h3>
              <ul className="space-y-2">
                {category.items.map((item, itemIndex) => (
                  <li key={itemIndex}>
                    <Link href="#" className="text-gray-600 hover:text-blue-600 transition-colors">
                      {item}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Frequently Asked Questions
          </h2>
          <div className="max-w-4xl mx-auto space-y-6">
            {faqData.map((faq, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  {faq.question}
                </h3>
                <p className="text-gray-600">
                  {faq.answer}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Contact Support */}
        <div className="bg-blue-50 rounded-xl p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Still Need Help?
          </h2>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            Can&apos;t find what you&apos;re looking for? Our support team is here to help you succeed with Bangla Chat Pro.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/contact"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Contact Support
            </Link>
            <a
              href="mailto:support@banglachatpro.com"
              className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Email Us
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
