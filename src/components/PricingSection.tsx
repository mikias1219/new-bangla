"use client";

import { useState } from "react";
import { Check } from "lucide-react";

const plans = [
  {
    name: "Free",
    price: { monthly: 0, yearly: 0 },
    description: "Perfect for trying out our AI chat features",
    features: [
      "Basic AI chat conversations",
      "Limited messages per day",
      "Community support",
      "Standard response time"
    ],
    cta: "Get Started",
    popular: false,
    trial: true
  },
  {
    name: "Basic",
    price: { monthly: 9.99, yearly: 99.99 },
    description: "Great for personal and light professional use",
    features: [
      "Advanced AI chat conversations",
      "Unlimited messages",
      "Voice message support",
      "Priority email support",
      "Custom conversation history"
    ],
    cta: "Start Basic Plan",
    popular: false,
    trial: false
  },
  {
    name: "Pro",
    price: { monthly: 19.99, yearly: 199.99 },
    description: "Ideal for professionals and growing businesses",
    features: [
      "Everything in Basic",
      "Custom AI model training",
      "API access for integrations",
      "Advanced analytics",
      "Phone support",
      "Multi-language support"
    ],
    cta: "Start Pro Plan",
    popular: true,
    trial: false
  },
  {
    name: "Enterprise",
    price: { monthly: 49.99, yearly: 499.99 },
    description: "For large organizations with advanced needs",
    features: [
      "Everything in Pro",
      "Dedicated account manager",
      "Custom integrations",
      "SLA guarantee",
      "On-premise deployment",
      "Advanced security features"
    ],
    cta: "Contact Sales",
    popular: false,
    trial: false
  }
];

export default function PricingSection() {
  const [isYearly, setIsYearly] = useState(false);

  return (
    <section id="pricing" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Choose Your Plan
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Start free and upgrade as you grow. All plans include our 14-day trial period.
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-4 mb-8">
            <span className={`text-sm ${!isYearly ? 'text-gray-900 font-semibold' : 'text-gray-600'}`}>
              Monthly
            </span>
            <button
              onClick={() => setIsYearly(!isYearly)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                isYearly ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  isYearly ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span className={`text-sm ${isYearly ? 'text-gray-900 font-semibold' : 'text-gray-600'}`}>
              Yearly
            </span>
            <span className="ml-2 text-sm text-green-600 font-semibold bg-green-100 px-2 py-1 rounded">
              Save 17%
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`bg-white rounded-xl p-8 shadow-sm hover:shadow-lg transition-shadow ${
                plan.popular ? 'ring-2 ring-blue-500 relative' : ''
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                <p className="text-gray-600 text-sm mb-4">{plan.description}</p>
                <div className="flex items-center justify-center">
                  <span className="text-4xl font-bold text-gray-900">
                    ${isYearly ? plan.price.yearly : plan.price.monthly}
                  </span>
                  {plan.price.monthly > 0 && (
                    <span className="text-gray-600 ml-1">
                      /{isYearly ? 'year' : 'month'}
                    </span>
                  )}
                </div>
                {plan.trial && (
                  <div className="mt-2 text-sm text-green-600 font-semibold">
                    14-day free trial
                  </div>
                )}
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
                    <span className="text-gray-700 text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <a
                href={plan.name === "Enterprise" ? "/contact" : "/register"}
                className={`w-full py-3 px-6 rounded-lg font-semibold text-center block transition-colors ${
                  plan.popular
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : plan.name === "Free"
                    ? 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                    : 'bg-white text-blue-600 border-2 border-blue-600 hover:bg-blue-50'
                }`}
              >
                {plan.cta}
              </a>
            </div>
          ))}
        </div>

        <div className="text-center mt-12">
          <p className="text-gray-600 mb-4">
            All plans include SSL encryption, regular backups, and 99.9% uptime guarantee.
          </p>
          <p className="text-sm text-gray-500">
            Prices are in USD. Cancel anytime. No setup fees or hidden charges.
          </p>
        </div>
      </div>
    </section>
  );
}
