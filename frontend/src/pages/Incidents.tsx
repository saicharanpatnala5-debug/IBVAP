import React from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { AlertBadge } from '../components/alerts/AlertBadge';
import { formatTimestamp } from '../utils/formatters';
import { MOCK_INCIDENTS } from '../services/api';
import { SEOHead } from '../components/common/SEOHead';
import { ShieldAlert, ArrowRight, Eye } from 'lucide-react';

interface IncidentsProps {
  onSelectIncident?: (id: string) => void;
}

export const Incidents: React.FC<IncidentsProps> = ({ onSelectIncident }) => {
  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto animate-fade-in">
      <SEOHead title="Fused Incident Dossiers" description="Multi-sensor correlated border breach incidents" />

      <Breadcrumbs items={[{ label: 'Fused Tactical Incidents', isCurrent: true }]} />

      <div className="space-y-4">
        {MOCK_INCIDENTS.map((inc) => (
          <div
            key={inc.incident_id}
            onClick={() => onSelectIncident && onSelectIncident(inc.incident_id)}
            className="rounded-3xl p-6 liquid-glass border border-slate-800 hover:border-slate-700 transition-all cursor-pointer group shadow-2xl"
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-2">
              <div className="flex items-center space-x-3">
                <AlertBadge severity={inc.severity} />
                <span className="text-xs font-mono font-bold text-white">
                  {inc.incident_id}
                </span>
                <span className="text-xs font-mono text-cyan-400">
                  PRIMARY: {inc.primary_camera_id}
                </span>
              </div>
              <span className="text-xs font-mono text-slate-500">
                {formatTimestamp(inc.created_at)}
              </span>
            </div>

            <h3 className="text-base font-bold text-white mt-4 group-hover:text-emerald-300 transition-colors">
              {inc.title}
            </h3>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">
              {inc.description}
            </p>

            <div className="mt-4 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
              <div className="flex items-center space-x-4 text-slate-400">
                <span>RISK SCORE: <strong className="text-rose-400">{inc.risk_score}</strong></span>
                <span>STATUS: <strong className="text-cyan-400">{inc.status}</strong></span>
              </div>

              <span className="text-emerald-400 flex items-center space-x-1 font-semibold group-hover:translate-x-1 transition-transform">
                <span>Inspect 5W Dossier</span>
                <ArrowRight className="w-4 h-4" />
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
