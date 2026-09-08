import React from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { ExplainableAICard } from '../components/incidents/ExplainableAICard';
import { IncidentTimeline } from '../components/incidents/IncidentTimeline';
import { EvidencePlayback } from '../components/video/EvidencePlayback';
import { MOCK_INCIDENTS } from '../services/api';
import { SEOHead } from '../components/common/SEOHead';
import { ShieldCheck, Download, Share2 } from 'lucide-react';

interface IncidentDetailsProps {
  incidentId?: string;
  onBack?: () => void;
}

export const IncidentDetails: React.FC<IncidentDetailsProps> = ({
  incidentId = 'INC-20260905-001',
  onBack,
}) => {
  const incident = MOCK_INCIDENTS[0];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto animate-fade-in">
      <SEOHead title={`Incident Dossier ${incidentId}`} description="5W Explainable AI breakdown and evidence chain" />

      <div className="flex items-center justify-between">
        <Breadcrumbs
          items={[
            { label: 'Fused Incidents', onClick: onBack },
            { label: incidentId, isCurrent: true },
          ]}
        />
        <div className="flex items-center space-x-3">
          <button className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-200 flex items-center space-x-1.5">
            <Share2 className="w-4 h-4 text-cyan-400" />
            <span>Forward to QRT</span>
          </button>
          <button className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-obsidian font-bold text-xs font-mono flex items-center space-x-1.5 shadow-tactical-glow">
            <Download className="w-4 h-4" />
            <span>Generate Defense Dossier</span>
          </button>
        </div>
      </div>

      <ExplainableAICard incident={incident} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <IncidentTimeline />
        <EvidencePlayback />
      </div>
    </div>
  );
};
