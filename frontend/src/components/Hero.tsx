import { useEffect, useRef, useState } from "react";
import Hls from "hls.js";
import gsap from "gsap";

export default function Hero() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLElement>(null);
  const [navScrolled, setNavScrolled] = useState(false);

  useEffect(() => {
    // HLS background video
    if (videoRef.current) {
      const src = "https://stream.mux.com/Aa02T7oM1wH5Mk5EEVDYhbZ1ChcdhRsS2m1NYyx4Ua1g.m3u8";
      if (Hls.isSupported()) {
        const hls = new Hls({ startPosition: -1 });
        hls.loadSource(src);
        hls.attachMedia(videoRef.current);
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          videoRef.current?.play().catch(() => {});
        });
      } else if (videoRef.current.canPlayType("application/vnd.apple.mpegurl")) {
        videoRef.current.src = src;
        videoRef.current.addEventListener("loadedmetadata", () => {
          videoRef.current?.play().catch(() => {});
        });
      }
    }
  }, []);

  useEffect(() => {
    // GSAP entrance timeline
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ delay: 0.2 });
      
      tl.fromTo(
        ".name-reveal",
        { y: 50, opacity: 0 },
        { y: 0, opacity: 1, duration: 1, stagger: 0.2, ease: "power3.out" }
      ).fromTo(
        ".blur-in",
        { filter: "blur(10px)", opacity: 0, y: 20 },
        { filter: "blur(0px)", opacity: 1, y: 0, duration: 0.8, stagger: 0.1, ease: "power2.out" },
        "-=0.5"
      );
    }, containerRef);

    return () => ctx.revert();
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      setNavScrolled(window.scrollY > 100);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <section id="home" ref={containerRef} className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Video */}
      <div className="absolute inset-0 z-0">
        <video
          ref={videoRef}
          muted
          loop
          playsInline
          className="w-full h-full object-cover opacity-40 mix-blend-screen"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-bg/50 via-bg/20 to-bg" />
      </div>

      {/* Nav Pill */}
      <nav
        className={`fixed top-6 left-1/2 -translate-x-1/2 z-50 transition-all duration-300 rounded-full border px-6 py-3 flex gap-8 items-center
          ${navScrolled ? "bg-surface/80 backdrop-blur-md border-stroke shadow-lg" : "bg-transparent border-transparent"}`}
      >
        <a href="#home" className="text-sm font-medium text-text-primary hover:text-accent transition">Command Center</a>
        <a href="#architecture" className="text-sm font-medium text-text-primary hover:text-accent transition">Architecture</a>
        <a href="#features" className="text-sm font-medium text-text-primary hover:text-accent transition">Features</a>
      </nav>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center text-center px-4 mt-16">
        <div className="mb-4 blur-in">
          <span className="text-sm uppercase tracking-[0.2em] text-muted border border-stroke rounded-full px-4 py-1">
            SSB / MHA Police-II
          </span>
        </div>
        
        <h1 className="text-5xl md:text-8xl font-display text-text-primary mb-6 overflow-hidden">
          <div className="name-reveal leading-tight">IBVAP</div>
          <div className="name-reveal leading-tight text-muted italic">Border Analytics</div>
        </h1>
        
        <p className="max-w-xl text-muted text-base md:text-lg mb-10 blur-in">
          Software-Defined AI Intelligence Transforming Legacy CCTV into Autonomous Border Surveillance.
        </p>
        
        <div className="flex gap-4 blur-in">
          <button className="bg-text-primary text-bg px-8 py-3 rounded-full font-medium hover:scale-105 transition">
            Launch Console
          </button>
          <button className="border border-stroke text-text-primary px-8 py-3 rounded-full font-medium hover:bg-surface transition">
            Documentation
          </button>
        </div>
      </div>
    </section>
  );
}
