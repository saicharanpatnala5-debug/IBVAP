import React, { useEffect, useRef } from "react";
import Hls from "hls.js";
import { motion } from "framer-motion";

export const HeroSection: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const videoSrc = "https://stream.mux.com/Aa02T7oM1wH5Mk5EEVDYhbZ1ChcdhRsS2m1NYyx4Ua1g.m3u8";

    if (Hls.isSupported()) {
      const hls = new Hls();
      hls.loadSource(videoSrc);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        video.play().catch(e => console.log("Play failed", e));
      });
      return () => {
        hls.destroy();
      };
    } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = videoSrc;
      video.addEventListener("loadedmetadata", () => {
        video.play().catch(e => console.log("Play failed", e));
      });
    }
  }, []);

  return (
    <section className="relative w-full h-screen overflow-hidden flex flex-col justify-center bg-bg">
      {/* Background Video */}
      <div className="absolute inset-0 z-0 opacity-40">
        <video
          ref={videoRef}
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover"
        />
      </div>

      {/* Grid Overlay */}
      <div className="absolute inset-0 z-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay pointer-events-none"></div>
      
      {/* Content */}
      <div className="relative z-10 container mx-auto px-6 h-full flex flex-col justify-center items-start">
        <motion.h1 
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
          className="font-display text-6xl md:text-8xl lg:text-9xl text-text-primary leading-[0.9] tracking-tighter"
        >
          Building <span className="accent-gradient-text italic pr-4">Digital</span><br />
          Experiences
        </motion.h1>
        
        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.5, ease: "easeOut" }}
          className="mt-8 font-body text-muted text-lg md:text-xl max-w-lg"
        >
          I specialize in crafting high-performance, accessible, and deeply interactive web applications.
        </motion.p>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center">
        <span className="font-body text-muted text-xs uppercase tracking-widest mb-2">Scroll</span>
        <div className="w-[1px] h-12 bg-stroke overflow-hidden relative">
          <div className="w-full h-1/2 accent-gradient animate-scroll-down"></div>
        </div>
      </div>
    </section>
  );
};
