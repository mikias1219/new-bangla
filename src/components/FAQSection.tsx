"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

const faqs = [
  {
    question: "How does the free trial work?",
    answer: "You can start with our 14-day free trial immediately after signing up. No credit card required. You'll have access to all Pro features during the trial period. If you decide to continue, you can choose any paid plan. If not, your account will automatically revert to the free plan."
  },
  {
    question: "Can I cancel my subscription anytime?",
    answer: "Absolutely! You can cancel your subscription at any time from your account settings. If you cancel during your billing cycle, you'll continue to have access to paid features until the end of your current billing period. No cancellation fees or penalties."
  },
  {
    question: "Is my data secure and private?",
    answer: "Yes, security is our top priority. All conversations are encrypted end-to-end, and we use bank-level security measures. We never share your personal data or conversation history with third parties. You can delete your data anytime from your account settings."
  },
  {
    question: "What languages does Bangla Chat Pro support?",
    answer: "We support multiple languages including Bangla, English, Hindi, Arabic, and many more. Our AI can understand and respond in your preferred language, and the voice features work with all supported languages."
  },
  {
    question: "Do you offer custom AI model training?",
    answer: "Yes! Our Pro and Enterprise plans include custom AI model training. You can train the AI on your specific industry, communication style, or knowledge base to get more personalized and relevant responses."
  },
  {
    question: "What's the difference between the Basic and Pro plans?",
    answer: "The Basic plan includes unlimited messages, voice support, and priority support. The Pro plan adds custom AI model training, API access, advanced analytics, and phone support. Pro is ideal for professionals and businesses with advanced needs."
  },
  {
    question: "Can I upgrade or downgrade my plan?",
    answer: "Yes, you can change your plan at any time. Upgrades take effect immediately, while downgrades take effect at the start of your next billing cycle. You'll be prorated for any plan changes."
  },
  {
    question: "Do you offer refunds?",
    answer: "We offer a 30-day money-back guarantee for all paid plans. If you're not satisfied with the service within the first 30 days, we'll provide a full refund. Contact our support team to initiate a refund."
  }
];

export default function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section id="faq" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-xl text-gray-600">
            Everything you need to know about Bangla Chat Pro
          </p>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm">
              <button
                onClick={() => toggleFAQ(index)}
                className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <span className="text-lg font-semibold text-gray-900">{faq.question}</span>
                {openIndex === index ? (
                  <ChevronUp className="w-5 h-5 text-gray-500" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-500" />
                )}
              </button>
              {openIndex === index && (
                <div className="px-6 pb-4">
                  <p className="text-gray-600 leading-relaxed">{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="text-center mt-12">
          <p className="text-gray-600 mb-4">
            Still have questions? We&apos;re here to help.
          </p>
          <a
            href="/contact"
            className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Contact Support
          </a>
        </div>
      </div>
    </section>
  );
}
