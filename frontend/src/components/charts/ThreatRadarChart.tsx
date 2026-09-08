import React from 'react';

export const ThreatRadarChart: React.FC = () => {
  const factors = [
    { label: 'Zone Intrusion', score: 95, max: 100, color: 'bg-rose-500' },
    { label: 'Night Context', score: 80, max: 100, color: 'bg-amber-500' },
    { label: 'Inward Direction', score: 85, max: 100, color: 'bg-rose-400' },
    { label: 'Loitering Dwell', score: 60, max: 100, color: 'bg-cyan-400' },
    { label: 'Unverified Vehicle', score: 75, max: 100, color: 'bg-orange-400' },
  ];

  return (
    <div className="rounded-2xl p-6 liquid-glass border border-slate-800">
      <h4 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider mb-4">
        CALIBRATED RISK FACTOR CONTRIBUTION
      </h4>
      <div className="space-y-3">
        {factors.map((f, idx) => (
          <div key={idx}>
            <div className="flex justify-between text-xs font-mono mb-1">
              <span className="text-slate-300">{f.label}</span>
              <span className="text-emerald-400 font-bold">{f.score} / {f.max}</span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className={`h-full ${f.color} rounded-full transition-all duration-500`}
                style={{ width: `${(f.score / f.max) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
