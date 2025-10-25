import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import IntegrationsSection from "@/components/IntegrationsSection";
import PricingSection from "@/components/PricingSection";
import TestimonialsSection from "@/components/TestimonialsSection";
import FAQSection from "@/components/FAQSection";
import Footer from "@/components/Footer";
import Navigation from "@/components/Navigation";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <Navigation />
      <div className="pt-16"> {/* Offset for fixed navbar */}
        <HeroSection />
        <FeaturesSection />
        <IntegrationsSection />
        <PricingSection />
        <TestimonialsSection />
        <FAQSection />
        <Footer />
      </div>
    </div>
  );
}
