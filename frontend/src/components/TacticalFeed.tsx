import { useLayoutEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

interface FeedItem {
  id: string;
  image: string;
  rotation: number;
}

const leftColumn: FeedItem[] = [
  { id: "e1", image: "https://images.unsplash.com/photo-1549488344-c116c906a6eb?q=80&w=600&auto=format&fit=crop", rotation: -4 },
  { id: "e2", image: "https://images.unsplash.com/photo-1584483766114-2cea6facdf57?q=80&w=600&auto=format&fit=crop", rotation: 3 },
  { id: "e3", image: "https://images.unsplash.com/photo-1614088998980-60b64eebbb72?q=80&w=600&auto=format&fit=crop", rotation: -2 },
];

const rightColumn: FeedItem[] = [
  { id: "e4", image: "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=600&auto=format&fit=crop", rotation: 4 },
  { id: "e5", image: "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?q=80&w=600&auto=format&fit=crop", rotation: -3 },
  { id: "e6", image: "https://images.unsplash.com/photo-1611095567219-8fa715ee7618?q=80&w=600&auto=format&fit=crop", rotation: 2 },
];

export default function TacticalFeed() {
  const sectionRef = useRef<HTMLElement>(null);
  const pinRef = useRef<HTMLDivElement>(null);
  const leftColRef = useRef<HTMLDivElement>(null);
  const rightColRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const section = sectionRef.current;
    const pinTarget = pinRef.current;
    if (!section || !pinTarget) return;

    const ctx = gsap.context(() => {
      // Pin the center content
      ScrollTrigger.create({
        trigger: section,
        start: "top top",
        end: "bottom bottom",
        pin: pinTarget,
        pinSpacing: false,
      });

      // Parallax columns
      if (leftColRef.current) {
        gsap.to(leftColRef.current, {
          yPercent: -15,
          ease: "none",
          scrollTrigger: {
            trigger: section,
            start: "top bottom",
            end: "bottom top",
            scrub: true,
          },
        });
      }

      if (rightColRef.current) {
        gsap.to(rightColRef.current, {
          yPercent: 15,
          ease: "none",
          scrollTrigger: {
            trigger: section,
            start: "top bottom",
            end: "bottom top",
            scrub: true,
          },
        });
      }
    }, section);

    const handleLoad = () => ScrollTrigger.refresh();
    window.addEventListener("load", handleLoad);

    return () => {
      window.removeEventListener("load", handleLoad);
      ctx.revert();
    };
  }, []);

  return (
    <section ref={sectionRef} className="relative min-h-[300vh] bg-bg">
      {/* Layer 1: Pinned Center */}
      <div
        ref={pinRef}
        className="h-screen flex flex-col items-center justify-center relative z-10 pointer-events-none"
      >
        <div className="pointer-events-auto flex flex-col items-center text-center px-6">
          <div className="flex items-center gap-2 mb-6">
            <span className="w-8 h-px bg-stroke" />
            <span className="text-xs text-muted uppercase tracking-[0.3em]">
              Surveillance Grid
            </span>
          </div>
          <h2 className="text-4xl md:text-6xl font-display italic text-text-primary mb-4">
            Tactical Feed
          </h2>
          <p className="text-sm md:text-base text-muted max-w-md mb-8">
            Real-time visual monitoring from forward-edge cameras, 
            analyzed by AI for threat detection.
          </p>
          <button className="rounded-full border-2 border-stroke px-6 py-3 text-sm text-text-primary hover:border-transparent hover:scale-105 transition bg-surface">
            Open Full Grid
          </button>
        </div>
      </div>

      {/* Layer 2: Parallax Columns */}
      <div className="absolute inset-0 z-20 flex items-start justify-center pt-[10vh] pointer-events-none">
        <div className="grid grid-cols-2 gap-12 md:gap-40 max-w-[1400px] w-full px-6">
          <div ref={leftColRef} className="flex flex-col gap-10">
            {leftColumn.map((item) => (
              <div
                key={item.id}
                className="aspect-square max-w-[320px] rounded-2xl overflow-hidden border border-stroke bg-surface pointer-events-auto shadow-xl"
                style={{ transform: `rotate(${item.rotation}deg)` }}
              >
                <img src={item.image} alt="" className="w-full h-full object-cover opacity-80 mix-blend-luminosity hover:mix-blend-normal transition-all duration-500" />
              </div>
            ))}
          </div>
          <div ref={rightColRef} className="flex flex-col gap-10 mt-24">
            {rightColumn.map((item) => (
              <div
                key={item.id}
                className="aspect-square max-w-[320px] rounded-2xl overflow-hidden border border-stroke bg-surface pointer-events-auto shadow-xl"
                style={{ transform: `rotate(${item.rotation}deg)` }}
              >
                <img src={item.image} alt="" className="w-full h-full object-cover opacity-80 mix-blend-luminosity hover:mix-blend-normal transition-all duration-500" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
