import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface LoadingScreenProps {
  onComplete: () => void;
}

const words = ["Perception", "Intelligence", "Surveillance"];

export default function LoadingScreen({ onComplete }: LoadingScreenProps) {
  const [progress, setProgress] = useState(0);
  const [wordIndex, setWordIndex] = useState(0);

  useEffect(() => {
    let startTimestamp: number | null = null;
    const duration = 2700;
    let animationFrameId: number;

    const animate = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const elapsed = timestamp - startTimestamp;
      const currentProgress = Math.min((elapsed / duration) * 100, 100);

      setProgress(currentProgress);

      if (currentProgress < 100) {
        animationFrameId = requestAnimationFrame(animate);
      } else {
        // Complete immediately after reaching 100
        setTimeout(onComplete, 100);
      }
    };

    animationFrameId = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationFrameId);
  }, [onComplete]);

  useEffect(() => {
    const wordInterval = setInterval(() => {
      setWordIndex((prev) => (prev + 1) % words.length);
    }, 900);

    return () => clearInterval(wordInterval);
  }, []);

  return (
    <motion.div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-bg"
      exit={{ y: "-100%", opacity: 0 }}
      transition={{ duration: 0.8, ease: [0.76, 0, 0.24, 1] }}
    >
      <div className="flex flex-col items-center">
        <div className="mb-8 h-12 overflow-hidden text-2xl font-body text-text-primary">
          <AnimatePresence mode="popLayout">
            <motion.div
              key={words[wordIndex]}
              initial={{ y: 40, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: -40, opacity: 0 }}
              transition={{ duration: 0.4, ease: "easeInOut" }}
            >
              {words[wordIndex]}
            </motion.div>
          </AnimatePresence>
        </div>
        
        <div className="font-display text-8xl md:text-9xl text-text-primary mb-8">
          {Math.floor(progress).toString().padStart(3, "0")}
        </div>

        <div className="h-1 w-64 bg-surface rounded-full overflow-hidden">
          <div
            className="h-full accent-gradient"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </motion.div>
  );
}
