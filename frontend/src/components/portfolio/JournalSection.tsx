import React, { useState } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";

const articles = [
  {
    id: 1,
    title: "The Future of Interaction Design",
    date: "Sep 2026",
    image: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=600",
  },
  {
    id: 2,
    title: "Mastering Framer Motion in React",
    date: "Aug 2026",
    image: "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&q=80&w=600",
  },
  {
    id: 3,
    title: "Building High-Performance WebGL",
    date: "Jul 2026",
    image: "https://images.unsplash.com/photo-1620121692029-d088224ddc74?auto=format&fit=crop&q=80&w=600",
  },
];

export const JournalSection: React.FC = () => {
  const [hoveredArticle, setHoveredArticle] = useState<number | null>(null);

  const cursorX = useMotionValue(0);
  const cursorY = useMotionValue(0);

  const springConfig = { damping: 25, stiffness: 120 };
  const cursorXSpring = useSpring(cursorX, springConfig);
  const cursorYSpring = useSpring(cursorY, springConfig);

  const handleMouseMove = (e: React.MouseEvent) => {
    // Offset the image so it's centered on the cursor
    cursorX.set(e.clientX - 150); 
    cursorY.set(e.clientY - 100);
  };

  return (
    <section 
      className="py-32 px-6 bg-bg relative overflow-hidden"
      onMouseMove={handleMouseMove}
    >
      <div className="container mx-auto max-w-5xl">
        <div className="mb-16 border-b border-stroke pb-6 flex justify-between items-end">
          <h2 className="font-display text-5xl text-text-primary">Journal</h2>
          <button className="font-body text-accent hover:text-text-primary transition-colors uppercase tracking-widest text-sm">
            View All
          </button>
        </div>

        <div className="flex flex-col">
          {articles.map((article) => (
            <div
              key={article.id}
              className="group border-b border-stroke py-8 flex justify-between items-center cursor-pointer transition-colors hover:border-accent"
              onMouseEnter={() => setHoveredArticle(article.id)}
              onMouseLeave={() => setHoveredArticle(null)}
            >
              <h3 className="font-display text-3xl md:text-5xl text-muted group-hover:text-text-primary transition-colors duration-300 transform group-hover:-translate-x-2">
                {article.title}
              </h3>
              <span className="font-body text-muted text-sm group-hover:text-accent transition-colors duration-300">
                {article.date}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Floating Image Reveal */}
      <motion.div
        className="fixed top-0 left-0 w-[300px] h-[200px] pointer-events-none z-50 overflow-hidden rounded-xl hidden md:block"
        style={{
          x: cursorXSpring,
          y: cursorYSpring,
          opacity: hoveredArticle !== null ? 1 : 0,
          scale: hoveredArticle !== null ? 1 : 0.8,
        }}
      >
        {articles.map((article) => (
          <img
            key={article.id}
            src={article.image}
            alt={article.title}
            className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-300 ${
              hoveredArticle === article.id ? "opacity-100" : "opacity-0"
            }`}
          />
        ))}
      </motion.div>
    </section>
  );
};
