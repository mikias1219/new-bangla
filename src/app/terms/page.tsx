import Link from "next/link";
import Navigation from "@/components/Navigation";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-white">
      <Navigation />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Terms of Service
          </h1>
          <p className="text-lg text-gray-600">
            Last updated: October 24, 2025
          </p>
        </div>

        <div className="prose prose-lg max-w-none">
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Agreement to Terms</h2>
            <p className="text-gray-700 mb-4">
              These Terms of Service (&ldquo;Terms&rdquo;) constitute a legally binding agreement between you and Bangla Chat Pro (&ldquo;we,&rdquo; &ldquo;our,&rdquo; or &ldquo;us&rdquo;) governing your access to and use of our AI-powered chat platform, website, and related services (collectively, the &ldquo;Service&rdquo;).
            </p>
            <p className="text-gray-700 mb-4">
              By accessing or using our Service, you agree to be bound by these Terms. If you do not agree to these Terms, you must not access or use our Service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Description of Service</h2>
            <p className="text-gray-700 mb-4">
              Bangla Chat Pro provides an AI-powered conversational platform that enables users to create, manage, and deploy intelligent chatbots and virtual assistants. Our services include:
            </p>
            <ul className="list-disc pl-6 text-gray-700 mb-4">
              <li>AI chat platform and dashboard</li>
              <li>Custom AI agent creation and management</li>
              <li>Integration with third-party platforms</li>
              <li>Analytics and reporting tools</li>
              <li>API access and developer tools</li>
              <li>Customer support and technical assistance</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">User Accounts</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Account Creation</h3>
            <p className="text-gray-700 mb-4">
              To use certain features of our Service, you must create an account. You agree to provide accurate, current, and complete information during the registration process and to update such information to keep it accurate, current, and complete.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Account Security</h3>
            <p className="text-gray-700 mb-4">
              You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. You must immediately notify us of any unauthorized use of your account or any other breach of security.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Account Termination</h3>
            <p className="text-gray-700 mb-4">
              We reserve the right to terminate or suspend your account at any time for violations of these Terms or for other reasons we deem necessary to protect our Service or users.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Acceptable Use Policy</h2>
            <p className="text-gray-700 mb-4">You agree to use our Service only for lawful purposes and in accordance with these Terms. You must not:</p>
            <ul className="list-disc pl-6 text-gray-700 mb-4">
              <li>Use the Service to violate any applicable laws or regulations</li>
              <li>Transmit harmful, threatening, abusive, or defamatory content</li>
              <li>Attempt to gain unauthorized access to our systems or other users&apos; accounts</li>
              <li>Use the Service to distribute malware, viruses, or other harmful code</li>
              <li>Interfere with or disrupt the Service or servers</li>
              <li>Reverse engineer, decompile, or disassemble our software</li>
              <li>Use automated tools to access the Service without permission</li>
              <li>Impersonate any person or entity or misrepresent your affiliation</li>
              <li>Use the Service for spam, harassment, or unsolicited communications</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Content and Data</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">User Content</h3>
            <p className="text-gray-700 mb-4">
              You retain ownership of any content you submit, post, or display on or through our Service (&ldquo;User Content&rdquo;). By submitting User Content, you grant us a worldwide, non-exclusive, royalty-free license to use, copy, modify, and display your content in connection with providing the Service.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">AI-Generated Content</h3>
            <p className="text-gray-700 mb-4">
              Content generated by our AI systems may be used for training and improving our models, unless you explicitly opt out of this usage in your account settings.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Data Storage and Backup</h3>
            <p className="text-gray-700 mb-4">
              While we implement security measures to protect your data, you are responsible for maintaining backups of your important data. We are not liable for any loss of data.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Pricing and Payment</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Subscription Plans</h3>
            <p className="text-gray-700 mb-4">
              Our Service is offered under various subscription plans with different features and usage limits. Pricing and features are subject to change with notice.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Billing and Payment</h3>
            <p className="text-gray-700 mb-4">
              You agree to pay all fees associated with your chosen subscription plan. Payments are processed securely through our payment providers. Failed payments may result in service suspension.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Refunds</h3>
            <p className="text-gray-700 mb-4">
              Refund requests are handled on a case-by-case basis. Generally, we offer refunds within 30 days of purchase for unused services. Custom enterprise agreements may have different refund policies.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Intellectual Property</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Our Intellectual Property</h3>
            <p className="text-gray-700 mb-4">
              The Service and its original content, features, and functionality are owned by Bangla Chat Pro and are protected by copyright, trademark, and other intellectual property laws.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Your Intellectual Property</h3>
            <p className="text-gray-700 mb-4">
              You retain ownership of your original content and intellectual property. By using our Service, you do not transfer any ownership rights to us.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">AI Model Usage</h3>
            <p className="text-gray-700 mb-4">
              Our AI models are proprietary and may not be copied, reproduced, or used outside of our Service without explicit permission.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Privacy and Data Protection</h2>
            <p className="text-gray-700 mb-4">
              Your privacy is important to us. Our collection and use of personal information is governed by our Privacy Policy, which is incorporated into these Terms by reference. By using our Service, you consent to our data practices as described in the Privacy Policy.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Third-Party Services</h2>
            <p className="text-gray-700 mb-4">
              Our Service may integrate with or contain links to third-party websites, services, or applications. We are not responsible for the availability, accuracy, or content of these third-party services. Your use of third-party services is subject to their respective terms and conditions.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Disclaimers and Limitations</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Service Availability</h3>
            <p className="text-gray-700 mb-4">
              While we strive for high availability, we do not guarantee that our Service will be uninterrupted or error-free. We may perform maintenance or updates that temporarily disrupt service.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">AI Limitations</h3>
            <p className="text-gray-700 mb-4">
              AI-generated content may not always be accurate, appropriate, or complete. You are responsible for reviewing and validating AI outputs before use.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Limitation of Liability</h3>
            <p className="text-gray-700 mb-4">
              To the maximum extent permitted by law, Bangla Chat Pro shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of the Service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Indemnification</h2>
            <p className="text-gray-700 mb-4">
              You agree to indemnify and hold harmless Bangla Chat Pro, its officers, directors, employees, and agents from any claims, damages, losses, or expenses arising from your use of the Service, violation of these Terms, or infringement of any rights of another party.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Termination</h2>
            <p className="text-gray-700 mb-4">
              Either party may terminate this agreement at any time. Upon termination, your right to use the Service ceases immediately, and we may delete your account and data in accordance with our data retention policies.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Governing Law</h2>
            <p className="text-gray-700 mb-4">
              These Terms shall be governed by and construed in accordance with the laws of Bangladesh, without regard to its conflict of law provisions. Any disputes arising from these Terms shall be resolved in the courts of Dhaka, Bangladesh.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Changes to Terms</h2>
            <p className="text-gray-700 mb-4">
              We reserve the right to modify these Terms at any time. We will notify users of material changes via email or through our Service. Continued use of the Service after changes constitutes acceptance of the new Terms.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Severability</h2>
            <p className="text-gray-700 mb-4">
              If any provision of these Terms is found to be unenforceable or invalid, that provision will be limited or eliminated to the minimum extent necessary, and the remaining provisions will remain in full force and effect.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Entire Agreement</h2>
            <p className="text-gray-700 mb-4">
              These Terms, together with our Privacy Policy, constitute the entire agreement between you and Bangla Chat Pro regarding the use of our Service and supersede all prior agreements.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Contact Information</h2>
            <p className="text-gray-700 mb-4">
              If you have any questions about these Terms, please contact us:
            </p>
            <div className="bg-gray-50 p-6 rounded-lg">
              <p className="text-gray-700 mb-2"><strong>Email:</strong> legal@banglachatpro.com</p>
              <p className="text-gray-700 mb-2"><strong>Phone:</strong> +1 (555) 123-4567</p>
              <p className="text-gray-700 mb-2"><strong>Address:</strong> Dhaka, Bangladesh</p>
              <p className="text-gray-700"><strong>Response Time:</strong> We aim to respond within 5 business days</p>
            </div>
          </section>
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
