import React, { useEffect, useState } from "react";
import { motion, useSpring, useTransform } from "framer-motion";

const Counter: React.FC<{ value: number; suffix?: string; title: string }> = ({ value, suffix = "", title }) => {
  const [isInView, setIsInView] = useState(false);
  const motionValue = useSpring(0, { duration: 2000, bounce: 0 });
  
  // Transform motion value to integer strings
  const displayValue = useTransform(motionValue, (latest) => Math.round(latest).toString());

  useEffect(() => {
    if (isInView) {
      motionValue.set(value);
    }
  }, [isInView, motionValue, value]);

  return (
    <div className="flex flex-col items-center justify-center p-8 border border-stroke rounded-2xl bg-bg/50 backdrop-blur-sm">
      <motion.div
        onViewportEnter={() => setIsInView(true)}
        viewport={{ once: true }}
        className="font-display text-6xl md:text-8xl text-text-primary accent-gradient-text mb-4"
      >
        <motion.span>{displayValue}</motion.span>
        <span>{suffix}</span>
      </motion.div>
      <span className="font-body text-muted uppercase tracking-widest text-sm">{title}</span>
    </div>
  );
};

export const StatsSection: React.FC = () => {
  return (
    <section className="py-32 px-6 bg-surface">
      <div className="container mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Counter value={40} suffix="+" title="Projects Completed" />
          <Counter value={100} suffix="%" title="Client Satisfaction" />
          <Counter value={5} suffix=" YRS" title="Industry Experience" />
        </div>
      </div>
    </section>
  );
};
