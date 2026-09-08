import { useEffect, useRef } from "react";
import gsap from "gsap";
import Hls from "hls.js";

const stats = [
  { value: "50,000", label: "Local Offline Queue Capacity" },
  { value: "5.19s", label: "System Test Suite Execution" },
  { value: "24/7", label: "Autonomous Border Surveillance" },
];

export default function Footer() {
  const marqueeRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (marqueeRef.current) {
      gsap.to(marqueeRef.current, {
        xPercent: -50,
        duration: 40,
        repeat: -1,
        ease: "none",
      });
    }

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

  return (
    <footer className="relative bg-bg pt-24 overflow-hidden border-t border-stroke mt-32">
      {/* Stats */}
      <div className="max-w-6xl mx-auto px-6 mb-32">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 border-y border-stroke py-12">
          {stats.map((stat, i) => (
            <div key={i} className="flex flex-col items-center text-center">
              <span className="text-5xl font-display italic text-text-primary mb-2">{stat.value}</span>
              <span className="text-sm text-muted uppercase tracking-widest">{stat.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Content with Video Background */}
      <div className="relative min-h-[500px] flex flex-col items-center justify-center">
        <div className="absolute inset-0 z-0">
          <video
            ref={videoRef}
            muted
            loop
            playsInline
            className="w-full h-full object-cover opacity-20 mix-blend-screen scale-y-[-1]"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-bg via-bg/80 to-transparent" />
        </div>

        <div className="relative z-10 w-full mb-16 overflow-hidden">
          <div className="flex w-[200%] whitespace-nowrap" ref={marqueeRef}>
            <div className="w-1/2 flex justify-around">
              <span className="text-8xl md:text-[10rem] font-display text-text-primary opacity-20">SECURE • AUTONOMOUS • </span>
            </div>
            <div className="w-1/2 flex justify-around">
              <span className="text-8xl md:text-[10rem] font-display text-text-primary opacity-20">SECURE • AUTONOMOUS • </span>
            </div>
          </div>
        </div>

        <div className="relative z-10 flex flex-col items-center gap-6 mb-16">
          <div className="flex items-center gap-3 bg-surface border border-stroke px-4 py-2 rounded-full">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs uppercase tracking-widest text-text-primary">System Online</span>
          </div>
          <a href="mailto:contact@ssb.gov.in" className="text-2xl text-text-primary hover:text-accent transition">
            Request Access Protocol
          </a>
        </div>
      </div>
    </footer>
  );
}
