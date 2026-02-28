import HeroSection from '../components/Landing/HeroSection';
import JiangSection from '../components/Landing/JiangSection';
import HowItWorksSection from '../components/Landing/HowItWorksSection';
import CTASection from '../components/Landing/CTASection';

export default function LandingPage() {
  return (
    <div>
      <HeroSection />
      <JiangSection />
      <HowItWorksSection />
      <CTASection />
    </div>
  );
}
