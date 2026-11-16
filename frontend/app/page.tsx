import Navbar from "../components/landing/Navbar";
import Hero from "../components/landing/Hero";
import Marquee from "../components/landing/Marquee";
import AgentSection from "../components/landing/AgentSection";
import WorkflowSection from "../components/landing/WorkflowSection";
import PlatformSection from "../components/landing/PlatformSection";
import TechStack from "../components/landing/TechStack";
import Footer from "../components/landing/Footer";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white text-black flex flex-col">
      <Navbar />
      <main className="flex-1">
        <Hero />
        <Marquee />
        <AgentSection />
        <WorkflowSection />
        <PlatformSection />
        <TechStack />
      </main>
      <Footer />
    </div>
  );
}
