import React from 'react';

export const HourlyBreachChart: React.FC = () => {
  const data = [
    { hour: '00h', val: 2 }, { hour: '02h', val: 7 }, { hour: '04h', val: 4 },
    { hour: '06h', val: 1 }, { hour: '08h', val: 0 }, { hour: '10h', val: 1 },
    { hour: '12h', val: 2 }, { hour: '14h', val: 0 }, { hour: '16h', val: 1 },
    { hour: '18h', val: 3 }, { hour: '20h', val: 5 }, { hour: '22h', val: 6 },
  ];

  const maxVal = 7;

  return (
    <div className="rounded-2xl p-6 liquid-glass border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider">
          24-HOUR BREACH FREQUENCY HISTOGRAM
        </h4>
        <span className="text-[10px] font-mono text-rose-400 font-bold">PEAK AT 02:00 UTC</span>
      </div>

      <div className="h-32 flex items-end justify-between space-x-2 pt-4">
        {data.map((d, idx) => {
          const pct = (d.val / maxVal) * 100;
          return (
            <div key={idx} className="flex-1 flex flex-col items-center group">
              <div
                className={`w-full rounded-t transition-all ${
                  d.val >= 5 ? 'bg-rose-500 shadow-alert-glow' : 'bg-emerald-500/60 group-hover:bg-emerald-400'
                }`}
                style={{ height: `${pct}%` }}
              />
              <span className="text-[9px] font-mono text-slate-500 mt-2">{d.hour}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
