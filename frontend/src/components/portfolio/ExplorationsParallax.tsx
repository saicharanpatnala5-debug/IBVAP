import React, { useLayoutEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

interface ExplorationItem {
  id: string;
  image: string;
  rotation: number;
}

// Map the project's actual images to the tilted 2-column layout from the reference
const leftColumn: ExplorationItem[] = [
  { id: "e1", image: "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&q=80&w=600", rotation: -4 },
  { id: "e2", image: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=600", rotation: 3 },
  { id: "e3", image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=600", rotation: -2 },
];

const rightColumn: ExplorationItem[] = [
  { id: "e4", image: "https://images.unsplash.com/photo-1620121692029-d088224ddc74?auto=format&fit=crop&q=80&w=600", rotation: 4 },
  { id: "e5", image: "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&q=80&w=600", rotation: -3 }, // Reusing images since we only have 4 in the project
  { id: "e6", image: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=600", rotation: 2 },
];

export const ExplorationsParallax: React.FC = () => {
  const sectionRef = useRef<HTMLElement>(null);
  const pinRef = useRef<HTMLDivElement>(null);
  const leftColRef = useRef<HTMLDivElement>(null);
  const rightColRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const section = sectionRef.current;
    const pinTarget = pinRef.current;
    if (!section || !pinTarget) return;

    const ctx = gsap.context(() => {
      // Pin the center content for the height of the section.
      ScrollTrigger.create({
        trigger: section,
        start: "top top",
        end: "bottom bottom",
        pin: pinTarget,
        pinSpacing: false,
      });

      // Parallax the two columns at different speeds
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

    // Refresh on load in case images or fonts shift layout
    const handleLoad = () => ScrollTrigger.refresh();
    window.addEventListener("load", handleLoad);

    return () => {
      window.removeEventListener("load", handleLoad);
      ctx.revert();
    };
  }, []);

  return (
    <section ref={sectionRef} className="relative min-h-[300vh] bg-bg">
      {/* Layer 1: pinned center content (z-10) */}
      <div
        ref={pinRef}
        className="h-screen flex flex-col items-center justify-center relative z-10 pointer-events-none"
      >
        <div className="pointer-events-auto flex flex-col items-center text-center px-6">
          <div className="flex items-center gap-2 mb-6">
            <span className="w-8 h-px bg-stroke" />
            <span className="text-xs text-muted uppercase tracking-[0.3em]">
              Explorations
            </span>
          </div>
          <h2 className="text-4xl md:text-6xl font-display italic text-text-primary mb-4">
            Visual playground
          </h2>
          <p className="text-sm md:text-base text-muted max-w-md mb-8">
            A running archive of visual experiments, motion studies and
            unreleased ideas.
          </p>
        </div>
      </div>

      {/* Layer 2: absolutely positioned parallax columns (z-20) */}
      <div className="absolute inset-0 z-20 flex items-start justify-center pt-[10vh]">
        <div className="grid grid-cols-2 gap-12 md:gap-40 max-w-[1400px] w-full px-6">
          <div ref={leftColRef} className="flex flex-col gap-10">
            {leftColumn.map((item) => (
              <div
                key={item.id}
                className="aspect-square max-w-[320px] rounded-2xl overflow-hidden border border-stroke bg-surface cursor-pointer"
                style={{ transform: `rotate(${item.rotation}deg)` }}
              >
                <img src={item.image} alt="" className="w-full h-full object-cover opacity-90 hover:opacity-100 transition-opacity" />
              </div>
            ))}
          </div>
          <div ref={rightColRef} className="flex flex-col gap-10 mt-24">
            {rightColumn.map((item) => (
              <div
                key={item.id}
                className="aspect-square max-w-[320px] rounded-2xl overflow-hidden border border-stroke bg-surface cursor-pointer"
                style={{ transform: `rotate(${item.rotation}deg)` }}
              >
                <img src={item.image} alt="" className="w-full h-full object-cover opacity-90 hover:opacity-100 transition-opacity" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
