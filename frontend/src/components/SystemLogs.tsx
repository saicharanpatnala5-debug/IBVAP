import { motion } from "framer-motion";

const logs = [
  { id: 1, date: "System Init", title: "Allocating zero-lag ring buffers for video ingestion.", status: "Online" },
  { id: 2, date: "AI Engine", title: "Loading YOLO26 and ByteTrack optimized models.", status: "Active" },
  { id: 3, date: "Edge Sync", title: "WAL offline queue established. 50k local capacity.", status: "Standby" },
];

export default function SystemLogs() {
  return (
    <section id="architecture" className="py-24 px-6 max-w-4xl mx-auto">
      <div className="mb-12">
        <h2 className="text-4xl font-display italic text-text-primary mb-4">Boot Sequence</h2>
      </div>
      
      <div className="flex flex-col gap-6">
        {logs.map((log, index) => (
          <motion.div
            key={log.id}
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="flex items-center justify-between border-b border-stroke pb-6 group cursor-pointer"
          >
            <div className="flex gap-8 items-center">
              <span className="text-muted text-sm">{log.date}</span>
              <h3 className="text-xl text-text-primary group-hover:text-accent transition">{log.title}</h3>
            </div>
            <span className="text-xs uppercase tracking-widest px-3 py-1 border border-stroke rounded-full">
              {log.status}
            </span>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
