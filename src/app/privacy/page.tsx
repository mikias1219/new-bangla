import Link from "next/link";
import Navigation from "@/components/Navigation";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-white">
      <Navigation />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Privacy Policy
          </h1>
          <p className="text-lg text-gray-600">
            Last updated: October 24, 2025
          </p>
        </div>

        <div className="prose prose-lg max-w-none">
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Introduction</h2>
            <p className="text-gray-700 mb-4">
              At Bangla Chat Pro (&ldquo;we,&rdquo; &ldquo;our,&rdquo; or &ldquo;us&rdquo;), we are committed to protecting your privacy and ensuring the security of your personal information. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our AI-powered chat platform and related services.
            </p>
            <p className="text-gray-700 mb-4">
              By using our services, you agree to the collection and use of information in accordance with this policy. If you do not agree with our policies and practices, please do not use our services.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Information We Collect</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Personal Information</h3>
            <p className="text-gray-700 mb-4">We may collect the following types of personal information:</p>
            <ul className="list-disc pl-6 text-gray-700 mb-4">
              <li><strong>Account Information:</strong> Name, email address, phone number, and password when you create an account</li>
              <li><strong>Profile Information:</strong> Profile picture, bio, and preferences you choose to provide</li>
              <li><strong>Communication Data:</strong> Messages, conversations, and feedback you send through our platform</li>
              <li><strong>Usage Data:</strong> Information about how you interact with our services, including features used and time spent</li>
              <li><strong>Device Information:</strong> IP address, browser type, operating system, and device identifiers</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Automatically Collected Information</h3>
            <p className="text-gray-700 mb-4">We automatically collect certain information when you use our services:</p>
            <ul className="list-disc pl-6 text-gray-700 mb-4">
              <li>Log data and analytics about your usage patterns</li>
              <li>Device and browser information</li>
              <li>Cookies and similar tracking technologies</li>
              <li>Location information (with your consent)</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">How We Use Your Information</h2>
            <p className="text-gray-700 mb-4">We use the information we collect for various purposes:</p>
            <ul className="list-disc pl-6 text-gray-700 mb-4">
              <li><strong>Service Provision:</strong> To provide, maintain, and improve our AI chat services</li>
              <li><strong>AI Training:</strong> To train and improve our AI models (with appropriate safeguards)</li>
              <li><strong>Customer Support:</strong> To respond to your inquiries and provide technical support</li>
              <li><strong>Personalization:</strong> To customize your experience and provide relevant content</li>
              <li><strong>Security:</strong> To protect against fraud, abuse, and unauthorized access</li>
              <li><strong>Legal Compliance:</strong> To comply with legal obligations and enforce our terms</li>
              <li><strong>Communication:</strong> To send you updates, newsletters, and marketing communications (with consent)</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Information Sharing and Disclosure</h2>
            <p className="text-gray-700 mb-4">We do not sell, trade, or rent your personal information to third parties. We may share your information in the following circumstances:</p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Service Providers</h3>
            <p className="text-gray-700 mb-4">
              We may share information with trusted third-party service providers who assist us in operating our platform, such as cloud hosting providers, payment processors, and analytics services. These providers are bound by confidentiality agreements and are not permitted to use your information for their own purposes.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Legal Requirements</h3>
            <p className="text-gray-700 mb-4">
              We may disclose your information if required by law, legal process, or government request. We may also disclose information to protect our rights, property, or safety, or that of our users or the public.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Business Transfers</h3>
            <p className="text-gray-700 mb-4">
              In the event of a merger, acquisition, or sale of assets, your information may be transferred as part of the transaction. We will notify you before your information is transferred and becomes subject to a different privacy policy.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Data Security</h2>
            <p className="text-gray-700 mb-4">
              We implement comprehensive security measures to protect your personal information:
            </p>
            <ul className="list-disc pl-6 text-gray-700 mb-4">
              <li>End-to-end encryption for all communications</li>
              <li>Secure data storage with regular backups</li>
              <li>Access controls and employee training</li>
              <li>Regular security audits and vulnerability assessments</li>
              <li>Incident response procedures</li>
            </ul>
            <p className="text-gray-700 mb-4">
              While we strive to protect your information, no method of transmission over the internet or electronic storage is 100% secure. We cannot guarantee absolute security but are committed to protecting your data to the fullest extent possible.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Data Retention</h2>
            <p className="text-gray-700 mb-4">
              We retain your personal information for as long as necessary to provide our services and fulfill the purposes outlined in this policy. Specifically:
            </p>
            <ul className="list-disc pl-6 text-gray-700 mb-4">
              <li>Account data is retained while your account is active and for a reasonable period thereafter</li>
              <li>Conversation data may be retained for service improvement and legal compliance</li>
              <li>Usage data is typically anonymized after 24 months</li>
              <li>Legal holds may extend retention periods as required</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Rights and Choices</h2>
            <p className="text-gray-700 mb-4">You have several rights regarding your personal information:</p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Access and Portability</h3>
            <p className="text-gray-700 mb-4">
              You can request access to your personal information and obtain a copy in a portable format.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Correction and Update</h3>
            <p className="text-gray-700 mb-4">
              You can update your account information and correct inaccurate data through your account settings.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Deletion</h3>
            <p className="text-gray-700 mb-4">
              You can request deletion of your personal information, subject to legal and legitimate business requirements.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">Opt-out</h3>
            <p className="text-gray-700 mb-4">
              You can opt out of marketing communications and certain data processing activities.
            </p>

            <p className="text-gray-700 mb-4">
              To exercise these rights, please contact us at privacy@banglachatpro.com or through your account settings.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Cookies and Tracking Technologies</h2>
            <p className="text-gray-700 mb-4">
              We use cookies and similar technologies to enhance your experience, analyze usage, and provide personalized content. You can control cookie preferences through your browser settings.
            </p>
            <ul className="list-disc pl-6 text-gray-700 mb-4">
              <li><strong>Essential Cookies:</strong> Required for basic platform functionality</li>
              <li><strong>Analytics Cookies:</strong> Help us understand how you use our services</li>
              <li><strong>Marketing Cookies:</strong> Used to deliver relevant advertisements</li>
              <li><strong>Preference Cookies:</strong> Remember your settings and preferences</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">International Data Transfers</h2>
            <p className="text-gray-700 mb-4">
              Your information may be transferred to and processed in countries other than your own. We ensure appropriate safeguards are in place for international data transfers, including standard contractual clauses and adequacy decisions.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Children&apos;s Privacy</h2>
            <p className="text-gray-700 mb-4">
              Our services are not intended for children under 13 years of age. We do not knowingly collect personal information from children under 13. If we become aware that we have collected such information, we will take steps to delete it promptly.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Changes to This Policy</h2>
            <p className="text-gray-700 mb-4">
              We may update this Privacy Policy from time to time. We will notify you of any material changes by posting the new policy on this page and updating the &ldquo;Last updated&rdquo; date. We encourage you to review this policy periodically.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Contact Us</h2>
            <p className="text-gray-700 mb-4">
              If you have any questions, concerns, or requests regarding this Privacy Policy or our data practices, please contact us:
            </p>
            <div className="bg-gray-50 p-6 rounded-lg">
              <p className="text-gray-700 mb-2"><strong>Email:</strong> privacy@banglachatpro.com</p>
              <p className="text-gray-700 mb-2"><strong>Phone:</strong> +1 (555) 123-4567</p>
              <p className="text-gray-700 mb-2"><strong>Address:</strong> Dhaka, Bangladesh</p>
              <p className="text-gray-700"><strong>Response Time:</strong> We aim to respond within 30 days</p>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">GDPR Compliance</h2>
            <p className="text-gray-700 mb-4">
              For users in the European Economic Area, we comply with the General Data Protection Regulation (GDPR). This includes providing data subject rights, maintaining records of processing activities, and conducting data protection impact assessments where required.
            </p>
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
