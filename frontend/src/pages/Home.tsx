import { useState } from "react";
import { AnimatePresence } from "framer-motion";
import LoadingScreen from "../components/LoadingScreen";
import Hero from "../components/Hero";
import FeaturesBento from "../components/FeaturesBento";
import SystemLogs from "../components/SystemLogs";
import TacticalFeed from "../components/TacticalFeed";
import Footer from "../components/Footer";

export default function Home() {
  const [loading, setLoading] = useState(true);

  return (
    <div className="relative bg-bg min-h-screen text-text-primary selection:bg-accent/30 overflow-x-hidden">
      <AnimatePresence>
        {loading && <LoadingScreen onComplete={() => setLoading(false)} />}
      </AnimatePresence>

      {!loading && (
        <main>
          <Hero />
          <FeaturesBento />
          <SystemLogs />
          <TacticalFeed />
          <Footer />
        </main>
      )}
    </div>
  );
}
