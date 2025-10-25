"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

export default function HeroSection() {
  const [currentDemo, setCurrentDemo] = useState(0);

  const demos = [
    {
      title: "E-commerce Customer Support",
      scenario: "Customer asks about order status",
      messages: [
        { type: "user", text: "আমার অর্ডার কোথায়? Order #12345" },
        { type: "ai", text: "আপনার অর্ডার #12345 প্রসেসিং অবস্থায় আছে এবং আগামী ২ দিনের মধ্যে ডেলিভারি হবে।\n\nYour order #12345 is being processed and will be delivered within 2 days." },
        { type: "user", text: "Thanks for the quick response!" },
        { type: "ai", text: "You're welcome! Is there anything else I can help you with?" }
      ]
    },
    {
      title: "WhatsApp Business Integration",
      scenario: "Customer contacts via WhatsApp",
      messages: [
        { type: "user", text: "Hi, I need help with my account" },
        { type: "ai", text: "Hello! I'd be happy to help with your account. Could you please provide your account email or phone number?" },
        { type: "user", text: "It's john@example.com" },
        { type: "ai", text: "Thank you! I can see your account. What specific issue are you facing today?" }
      ]
    },
    {
      title: "Voice Call Support (IVR)",
      scenario: "Customer calls for support",
      messages: [
        { type: "system", text: "📞 Incoming call from +8801712345678" },
        { type: "ai", text: "স্বাগতম! অনুগ্রহ করে বলুন আপনি কী সাহায্য চান?\n\nWelcome! Please tell me how can I help you?" },
        { type: "user", text: "I need to speak to customer service" },
        { type: "ai", text: "আমি আপনাকে কাস্টমার সার্ভিস এর সাথে সংযোগিত করছি। অনুগ্রহ করে অপেক্ষা করুন।\n\nConnecting you with customer service. Please wait." }
      ]
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentDemo((prev) => (prev + 1) % demos.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 animate-pulse"></div>
        <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div className="absolute top-0 -right-4 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left side - Text content */}
          <div className="text-center lg:text-left">
            <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2 mb-8">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-white text-sm font-medium">AI-Powered Customer Service Platform</span>
            </div>

            <h1 className="text-5xl sm:text-7xl font-bold text-white mb-6 leading-tight">
              Bangla Chat
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 block">
                Pro
              </span>
            </h1>

            <p className="text-xl sm:text-2xl text-gray-300 mb-8 max-w-2xl mx-auto lg:mx-0 leading-relaxed">
              Transform your customer service with intelligent AI agents that speak Bangla,
              integrate with all your favorite platforms, and handle both voice and text conversations.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start mb-12">
              <Link
                href="/register"
                className="group relative bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:from-blue-600 hover:to-purple-700 transition-all duration-300 shadow-2xl hover:shadow-blue-500/25 transform hover:scale-105"
              >
                <span className="relative z-10">Start Free Trial</span>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-500 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </Link>
              <Link
                href="#demo"
                className="bg-white/10 backdrop-blur-sm text-white border border-white/20 px-8 py-4 rounded-xl text-lg font-semibold hover:bg-white/20 transition-all duration-300"
              >
                Watch Demo
              </Link>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 max-w-md mx-auto lg:mx-0">
              <div className="text-center">
                <div className="text-3xl font-bold text-white mb-1">10K+</div>
                <div className="text-gray-400 text-sm">Active Users</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white mb-1">50K+</div>
                <div className="text-gray-400 text-sm">Conversations</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white mb-1">99.9%</div>
                <div className="text-gray-400 text-sm">Uptime</div>
              </div>
            </div>
          </div>

          {/* Right side - Interactive Demo */}
          <div className="relative">
            <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl">
              {/* Demo Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <div className="font-semibold text-white">{demos[currentDemo].title}</div>
                    <div className="text-sm text-gray-300">{demos[currentDemo].scenario}</div>
                  </div>
                </div>
                <div className="flex gap-2">
                  {demos.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentDemo(index)}
                      className={`w-2 h-2 rounded-full transition-all duration-300 ${
                        index === currentDemo ? 'bg-blue-400' : 'bg-white/30'
                      }`}
                    />
                  ))}
                </div>
              </div>

              {/* Chat Messages */}
              <div className="space-y-4 mb-6 max-h-80 overflow-y-auto">
                {demos[currentDemo].messages.map((message, index) => (
                  <div key={index} className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    {message.type !== 'user' && message.type !== 'system' && (
                      <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                      </div>
                    )}
                    {message.type === 'system' && (
                      <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-xs text-white">📞</span>
                      </div>
                    )}
                    <div className={`max-w-xs px-4 py-2 rounded-2xl ${
                      message.type === 'user'
                        ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white'
                        : message.type === 'system'
                        ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'
                        : 'bg-white/10 backdrop-blur-sm text-gray-100 border border-white/20'
                    }`}>
                      <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                    </div>
                    {message.type === 'user' && (
                      <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-xs text-white">👤</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Integration Icons */}
              <div className="flex items-center justify-between pt-4 border-t border-white/20">
                <div className="flex items-center gap-3">
                  <div className="text-xs text-gray-400">Integrates with:</div>
                  <div className="flex gap-2">
                    <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                      <span className="text-xs text-white">📱</span>
                    </div>
                    <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                      <span className="text-xs text-white">💬</span>
                    </div>
                    <div className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center">
                      <span className="text-xs text-white">📘</span>
                    </div>
                    <div className="w-6 h-6 bg-pink-500 rounded-full flex items-center justify-center">
                      <span className="text-xs text-white">📷</span>
                    </div>
                  </div>
                </div>
                <div className="text-xs text-green-400 font-medium">Live Demo</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes blob {
          0% { transform: translate(0px, 0px) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
          100% { transform: translate(0px, 0px) scale(1); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </section>
  );
}
