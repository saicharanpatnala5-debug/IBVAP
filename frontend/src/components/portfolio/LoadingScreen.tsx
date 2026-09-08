import React, { useEffect, useRef } from "react";
import gsap from "gsap";

export const LoadingScreen: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const tl = gsap.timeline({
      onComplete,
    });

    tl.to(textRef.current, {
      opacity: 1,
      y: 0,
      duration: 1,
      ease: "power3.out",
    })
      .to(textRef.current, {
        opacity: 0,
        y: -20,
        duration: 0.8,
        ease: "power3.in",
        delay: 0.5,
      })
      .to(containerRef.current, {
        yPercent: -100,
        duration: 1,
        ease: "power4.inOut",
      });

    return () => {
      tl.kill();
    };
  }, [onComplete]);

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-bg"
    >
      <div
        ref={textRef}
        className="opacity-0 translate-y-[20px] text-text-primary font-display text-4xl sm:text-5xl md:text-6xl tracking-tight"
      >
        Creative Developer
      </div>
    </div>
  );
};

