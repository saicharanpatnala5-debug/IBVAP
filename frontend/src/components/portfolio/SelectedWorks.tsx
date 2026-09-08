import React from "react";
import { motion } from "framer-motion";

const projects = [
  {
    id: 1,
    title: "E-Commerce Platform",
    category: "Web Development",
    image: "https://images.unsplash.com/photo-1661956602116-aa6865609028?auto=format&fit=crop&q=80&w=800",
    colSpan: "col-span-1 md:col-span-2",
    rowSpan: "row-span-2",
  },
  {
    id: 2,
    title: "Fintech Dashboard",
    category: "UI/UX Design",
    image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=800",
    colSpan: "col-span-1",
    rowSpan: "row-span-1",
  },
  {
    id: 3,
    title: "Healthcare App",
    category: "Mobile App",
    image: "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&q=80&w=800",
    colSpan: "col-span-1",
    rowSpan: "row-span-1",
  },
  {
    id: 4,
    title: "AI Image Generator",
    category: "Machine Learning",
    image: "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=800",
    colSpan: "col-span-1 md:col-span-3",
    rowSpan: "row-span-1",
  },
];

export const SelectedWorks: React.FC = () => {
  return (
    <section className="py-32 px-6 bg-surface">
      <div className="container mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8 }}
          className="mb-16"
        >
          <h2 className="font-display text-5xl md:text-7xl text-text-primary">
            Selected Works
          </h2>
          <p className="font-body text-muted mt-4 text-lg">A showcase of my recent projects.</p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 auto-rows-[300px] gap-6">
          {projects.map((project, index) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className={`group relative overflow-hidden rounded-2xl bg-bg border border-stroke transition-colors hover:border-transparent ${project.colSpan} ${project.rowSpan}`}
            >
              {/* Hover Gradient Border (using a pseudo-element approach via inner div) */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 accent-gradient p-[1px] rounded-2xl z-20 pointer-events-none">
                <div className="w-full h-full bg-bg rounded-2xl"></div>
              </div>

              <img
                src={project.image}
                alt={project.title}
                className="absolute inset-0 w-full h-full object-cover opacity-50 group-hover:opacity-80 transition-all duration-700 group-hover:scale-105 z-0"
              />
              
              <div className="absolute inset-0 bg-gradient-to-t from-bg/90 via-bg/20 to-transparent z-10" />

              <div className="absolute bottom-0 left-0 p-8 z-30">
                <p className="font-body text-accent text-sm mb-2 uppercase tracking-wider">{project.category}</p>
                <h3 className="font-display text-3xl text-text-primary">{project.title}</h3>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
