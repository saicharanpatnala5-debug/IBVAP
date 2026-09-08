import React from "react";
import { motion } from "framer-motion";

export const ContactFooter: React.FC = () => {
  return (
    <footer className="bg-bg pt-32 pb-12 overflow-hidden border-t border-stroke relative">
      <div className="container mx-auto px-6 mb-24">
        <div className="flex flex-col md:flex-row justify-between items-end">
          <div>
            <h2 className="font-display text-5xl md:text-8xl text-text-primary leading-[0.9]">
              Let's create <br />
              <span className="italic text-muted">together</span>
            </h2>
          </div>
          <div className="mt-12 md:mt-0 flex flex-col gap-4">
            <a 
              href="mailto:hello@example.com"
              className="font-body text-xl text-text-primary hover:text-accent transition-colors border-b border-transparent hover:border-accent inline-block pb-1"
            >
              hello@example.com
            </a>
            <div className="flex gap-6 mt-4">
              {['Twitter', 'LinkedIn', 'GitHub'].map((social) => (
                <a 
                  key={social} 
                  href="#" 
                  className="font-body text-muted text-sm uppercase tracking-widest hover:text-text-primary transition-colors"
                >
                  {social}
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Endless Marquee */}
      <div className="w-full relative flex overflow-x-hidden border-y border-stroke py-6 bg-surface">
        <motion.div
          className="flex whitespace-nowrap"
          animate={{ x: ["0%", "-50%"] }}
          transition={{
            repeat: Infinity,
            ease: "linear",
            duration: 15,
          }}
        >
          {Array(4).fill("AVAILABLE FOR FREELANCE WORK — ").map((text, i) => (
            <span key={i} className="font-display text-4xl mx-4 text-text-primary tracking-wide">
              {text}
            </span>
          ))}
        </motion.div>
      </div>

      <div className="container mx-auto px-6 mt-12 flex justify-between items-center text-sm font-body text-muted">
        <p>&copy; 2026 Creative Developer.</p>
        <p>Built with React & GSAP</p>
      </div>
    </footer>
  );
};
