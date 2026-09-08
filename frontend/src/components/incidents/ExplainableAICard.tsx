import React from 'react';
import { Incident } from '../../types';
import { AlertBadge } from '../alerts/AlertBadge';

interface ExplainableAICardProps {
  incident: Incident;
}

export const ExplainableAICard: React.FC<ExplainableAICardProps> = ({ incident }) => {
  const { what, who, where, when, why } = incident.explainable_breakdown;

  return (
    <div className="rounded-2xl p-6 liquid-glass border border-slate-800 shadow-2xl">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
        <div>
          <span className="text-[10px] font-mono uppercase tracking-widest text-emerald-400 font-bold">
            EXPLAINABLE AI REASONING ENGINE (5W TRANSPARENCY)
          </span>
          <h3 className="text-lg font-bold text-white mt-0.5">{incident.title}</h3>
        </div>
        <div className="flex items-center space-x-2">
          <AlertBadge severity={incident.severity} />
          <span className="text-xs font-mono font-bold text-slate-300">
            SCORE: {incident.risk_score}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono mb-6">
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-slate-500 uppercase text-[10px] font-bold block mb-1">WHAT</span>
          <span className="text-slate-200">{what}</span>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-slate-500 uppercase text-[10px] font-bold block mb-1">WHO</span>
          <span className="text-cyan-300">{who}</span>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-slate-500 uppercase text-[10px] font-bold block mb-1">WHERE</span>
          <span className="text-slate-200">{where}</span>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-slate-500 uppercase text-[10px] font-bold block mb-1">WHEN</span>
          <span className="text-slate-200">{when}</span>
        </div>
      </div>

      <div className="pt-4 border-t border-slate-800">
        <span className="text-xs font-mono uppercase font-bold text-slate-300 block mb-3">
          WHY: CALIBRATED THREAT FACTOR DECOMPOSITION
        </span>

        <div className="space-y-2">
          {why.map((item, idx) => (
            <div key={idx} className="flex items-center justify-between text-xs font-mono p-2 rounded-lg bg-slate-900/40 border border-slate-800/80">
              <span className="text-slate-300">{item.factor}</span>
              <span className="text-emerald-400 font-bold">{item.contribution}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
