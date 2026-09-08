import React from 'react';

export const RiskDistributionChart: React.FC = () => {
  const slices = [
    { label: 'CRITICAL (120+)', pct: 15, color: 'text-rose-500 bg-rose-500' },
    { label: 'HIGH (90-119)', pct: 25, color: 'text-orange-500 bg-orange-500' },
    { label: 'MEDIUM (60-89)', pct: 35, color: 'text-amber-500 bg-amber-500' },
    { label: 'LOW (30-59)', pct: 25, color: 'text-emerald-500 bg-emerald-500' },
  ];

  return (
    <div className="rounded-2xl p-6 liquid-glass border border-slate-800">
      <h4 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider mb-4">
        THREAT SEVERITY DISTRIBUTION (30 DAYS)
      </h4>

      <div className="flex items-center space-x-2 mb-4 h-3 rounded-full overflow-hidden">
        {slices.map((s, idx) => (
          <div key={idx} className={`h-full ${s.color.split(' ')[1]}`} style={{ width: `${s.pct}%` }} />
        ))}
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs font-mono">
        {slices.map((s, idx) => (
          <div key={idx} className="flex items-center space-x-2">
            <span className={`w-2.5 h-2.5 rounded-full ${s.color.split(' ')[1]}`} />
            <span className="text-slate-300">{s.label}: <strong>{s.pct}%</strong></span>
          </div>
        ))}
      </div>
    </div>
  );
};
