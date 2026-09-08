import React, { useState } from "react";
import { LoadingScreen } from "./LoadingScreen";
import { HeroSection } from "./HeroSection";
import { SelectedWorks } from "./SelectedWorks";
import { JournalSection } from "./JournalSection";
import { ExplorationsParallax } from "./ExplorationsParallax";
import { StatsSection } from "./StatsSection";
import { ContactFooter } from "./ContactFooter";

export const PortfolioLandingPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);

  return (
    <div className="bg-bg min-h-screen text-text-primary font-body antialiased selection:bg-surface selection:text-accent">
      {isLoading && <LoadingScreen onComplete={() => setIsLoading(false)} />}
      
      {/* Hide scrollbar on the main wrapper but allow scrolling */}
      <main className={`relative w-full h-full ${isLoading ? 'h-screen overflow-hidden' : ''}`}>
        <HeroSection />
        <SelectedWorks />
        <JournalSection />
        <ExplorationsParallax />
        <StatsSection />
        <ContactFooter />
      </main>
    </div>
  );
};
