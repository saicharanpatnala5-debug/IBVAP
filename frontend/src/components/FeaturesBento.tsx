import { motion } from "framer-motion";

const features = [
  {
    id: 1,
    title: "Risk Scoring Engine",
    desc: "Calculates calibrated threat probabilities across multi-factor inputs (Zones, Curfew, Loitering).",
    span: "md:col-span-2",
  },
  {
    id: 2,
    title: "8-State Kalman Tracker",
    desc: "Tracks targets continuously through occlusions and erratic movement.",
    span: "md:col-span-1",
  },
  {
    id: 3,
    title: "Topology Handoff",
    desc: "Predicts multi-camera transitions via weighted directed graphs.",
    span: "md:col-span-1",
  },
  {
    id: 4,
    title: "Air-Gapped Resiliency",
    desc: "Autonomous SQLite WAL offline queue with priority 4-tier upstream syncing.",
    span: "md:col-span-2",
  },
];

export default function FeaturesBento() {
  return (
    <section id="features" className="py-24 px-6 max-w-6xl mx-auto">
      <div className="mb-16">
        <h2 className="text-4xl md:text-6xl font-display italic text-text-primary mb-4">Core Pillars</h2>
        <p className="text-muted max-w-md">Architectural foundation built for reliable forward-edge deployment.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map((feat) => (
          <motion.div
            key={feat.id}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className={`group relative overflow-hidden rounded-3xl bg-surface border border-stroke p-8 min-h-[300px] flex flex-col justify-end ${feat.span} cursor-pointer`}
          >
            {/* Hover overlay gradient */}
            <div className="absolute inset-0 bg-gradient-to-t from-bg/90 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 z-10" />
            
            {/* Background scaling on hover */}
            <div className="absolute inset-0 bg-stroke/20 scale-100 group-hover:scale-105 transition-transform duration-700 ease-out z-0" />

            <div className="relative z-20">
              <div className="mb-4 inline-block rounded-full bg-bg border border-stroke px-4 py-1 text-xs uppercase tracking-widest text-muted group-hover:border-accent transition-colors duration-300">
                Pillar 0{feat.id}
              </div>
              <h3 className="text-2xl font-medium text-text-primary mb-2">{feat.title}</h3>
              <p className="text-muted text-sm max-w-sm">{feat.desc}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
