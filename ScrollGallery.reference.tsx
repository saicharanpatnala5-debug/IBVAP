/**
 * Reference implementation — pinned parallax "Explorations" section.
 *
 * This targets the exact failure points that usually break this pattern in a
 * React + Vite + GSAP setup:
 *
 * 1. Plugin registered once, at module scope, before any ScrollTrigger use.
 * 2. DOM measurement/setup happens in useLayoutEffect (before paint), not useEffect.
 * 3. Everything is created inside gsap.context() and torn down with ctx.revert()
 *    on cleanup. Without this, React 18 StrictMode's dev-only mount -> unmount ->
 *    remount cycle leaves duplicate or dead ScrollTriggers and the pin does nothing.
 * 4. ScrollTrigger.refresh() runs after window 'load', because late-loading images
 *    or the Instrument Serif webfont shift section height and desync the pin's
 *    start/end points if you don't re-measure.
 * 5. No ancestor of <section> here should have overflow:hidden/auto or a transform —
 *    any of those create a new containing block and silently break the pin. Check
 *    your app's root layout wrapper if pinning still doesn't work.
 *
 * Adapt the content, image sources, and class names to the real project — this file
 * is meant to be read and understood, not copy-pasted as-is.
 */

import { useLayoutEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

interface ExplorationItem {
  id: string;
  image: string;
  rotation: number;
}

const leftColumn: ExplorationItem[] = [
  { id: "e1", image: "/explorations/1.jpg", rotation: -4 },
  { id: "e2", image: "/explorations/2.jpg", rotation: 3 },
  { id: "e3", image: "/explorations/3.jpg", rotation: -2 },
];

const rightColumn: ExplorationItem[] = [
  { id: "e4", image: "/explorations/4.jpg", rotation: 4 },
  { id: "e5", image: "/explorations/5.jpg", rotation: -3 },
  { id: "e6", image: "/explorations/6.jpg", rotation: 2 },
];

export default function ExplorationsSection() {
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

      // Parallax the two columns at different speeds as the section scrolls past.
      // yPercent is relative to each column's own height, so it stays
      // resolution-independent instead of hard-coding pixel offsets.
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

    // Late-loading images/fonts shift layout after ScrollTrigger has already
    // measured it — re-measure once everything has actually loaded.
    const handleLoad = () => ScrollTrigger.refresh();
    window.addEventListener("load", handleLoad);

    return () => {
      window.removeEventListener("load", handleLoad);
      ctx.revert(); // kills every tween/ScrollTrigger created inside ctx
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
          <a
            href="https://dribbble.com"
            target="_blank"
            rel="noreferrer"
            className="rounded-full border-2 border-stroke px-6 py-3 text-sm text-text-primary hover:border-transparent hover:scale-105 transition"
          >
            View on Dribbble
          </a>
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
                <img src={item.image} alt="" className="w-full h-full object-cover" />
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
                <img src={item.image} alt="" className="w-full h-full object-cover" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
