import React from 'react';
import { Cpu, Network, ShieldAlert, ArrowRight } from 'lucide-react';

export const FeatureCards: React.FC = () => {
  const cards = [
    {
      icon: Cpu,
      title: 'AI Edge Inference',
      tag: '< 15ms LATENCY',
      description: 'Executes YOLOv8 object detection and ByteTrack multi-target correlation directly on low-power Jetson edge devices without cloud dependence.',
      borderGlow: 'hover:border-emerald-500/50'
    },
    {
      icon: Network,
      title: 'Multi-Camera Topology Graph',
      tag: 'DIRECTED RE-ID',
      description: 'Probabilistic topological camera transitions map intruder trajectories across border gates, physical fence zones, and internal armory corridors.',
      borderGlow: 'hover:border-cyan-500/50'
    },
    {
      icon: ShieldAlert,
      title: 'Explainable AI Threat Cards',
      tag: '5W TRANSPARENCY',
      description: 'Zero black-box decisions — calibrated risk scoring decomposes every incident into What, Who, Where, When, and Why with mathematical factor weights.',
      borderGlow: 'hover:border-rose-500/50'
    }
  ];

  return (
    <section className="py-8 px-4 max-w-7xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {cards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className={`rounded-2xl p-6 liquid-glass border border-slate-800/80 transition-all duration-300 hover:-translate-y-1 ${card.borderGlow} group`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 flex items-center justify-center text-emerald-400 group-hover:text-cyan-300 transition-colors">
                  <Icon className="w-5 h-5" />
                </div>
                <span className="text-[10px] font-mono uppercase tracking-widest px-2 py-0.5 rounded bg-slate-800/80 text-cyan-400 border border-slate-700 font-bold">
                  {card.tag}
                </span>
              </div>

              <h3 className="text-base font-bold text-white mb-2">{card.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">{card.description}</p>

              <div className="flex items-center space-x-1.5 text-xs font-mono text-emerald-400 font-semibold group-hover:text-cyan-300">
                <span>Inspect Architecture</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1.5 transition-transform duration-200" />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
