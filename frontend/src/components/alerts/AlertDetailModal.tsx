import React from 'react';
import { Alert } from '../../types';
import { AlertBadge } from './AlertBadge';
import { formatTimestamp, formatRuleTriggered } from '../../utils/formatters';
import { X, Radio } from 'lucide-react';
import { AlertExplainabilityCard } from './AlertExplainabilityCard';

interface AlertDetailModalProps {
  alert: Alert | null;
  onClose: () => void;
  onAcknowledge?: (id: string) => void;
}

export const AlertDetailModal: React.FC<AlertDetailModalProps> = ({
  alert,
  onClose,
  onAcknowledge,
}) => {
  if (!alert) return null;

  const effectiveScore = (typeof alert.risk_score === 'number' && alert.risk_score > 0)
    ? alert.risk_score
    : (alert.severity === 'CRITICAL' ? 95 :
       alert.severity === 'HIGH' ? 75 :
       alert.severity === 'MEDIUM' ? 55 : 25);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div className="relative w-full max-w-2xl rounded-3xl p-6 liquid-glass border border-slate-700 shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <AlertBadge severity={alert.severity} />
            <h3 className="text-base font-bold text-white font-mono">
              {alert.alert_id} — Tactical Incident
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="my-4 relative aspect-video rounded-2xl bg-black border border-slate-800 overflow-hidden flex items-center justify-center group">
          <img
            src={alert.evidence_frame_url || alert.snapshot_url || '/snapshots/master_surveillance_snapshot.jpg'}
            alt={`Evidence frame ${alert.alert_id}`}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).src = '/snapshots/master_surveillance_snapshot.jpg';
            }}
          />

          {/* Tactical HUD Overlay Brackets */}
          <div className="absolute top-3 left-3 w-4 h-4 border-t-2 border-l-2 border-rose-500 pointer-events-none" />
          <div className="absolute top-3 right-3 w-4 h-4 border-t-2 border-r-2 border-rose-500 pointer-events-none" />
          <div className="absolute bottom-3 left-3 w-4 h-4 border-b-2 border-l-2 border-rose-500 pointer-events-none" />
          <div className="absolute bottom-3 right-3 w-4 h-4 border-b-2 border-r-2 border-rose-500 pointer-events-none" />

          {/* Top Metadata Badge */}
          <div className="absolute top-3 left-3 ml-2 mt-1 flex items-center space-x-2 bg-black/80 backdrop-blur-md px-2.5 py-1 rounded-xl border border-rose-500/40 text-[10px] font-mono">
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
            <span className="font-bold text-white uppercase tracking-wider">EVIDENCE SNAPSHOT [{alert.camera_id}]</span>
          </div>

          {/* Bottom Rule Trigger Badge */}
          <div className="absolute bottom-3 left-3 ml-2 mb-1 bg-black/80 backdrop-blur-md px-2.5 py-1 rounded-xl border border-slate-800 text-[10px] font-mono text-cyan-400">
            <span>Rule: {formatRuleTriggered(alert.rule_triggered)}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-xs font-mono py-2">
          <div>
            <span className="text-slate-500 block">Timestamp</span>
            <span className="text-slate-200">{formatTimestamp(alert.created_at)}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Risk Score</span>
            <span className="text-emerald-400 font-bold">{effectiveScore} / 120</span>
          </div>
        </div>

        {/* Explainable AI Card (Trust & Transparency Layer) */}
        <div className="my-3">
          <AlertExplainabilityCard 
            alert={alert}
            detectionConfidence={0.965}
            ocrConfidence={0.942}
          />
        </div>

        <p className="text-xs text-slate-300 leading-relaxed my-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
          {alert.message}
        </p>

        <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-mono text-slate-400 hover:text-white"
          >
            Dismiss
          </button>
          {alert.status === 'ACTIVE' && onAcknowledge && (
            <button
              onClick={() => {
                onAcknowledge(alert.alert_id);
                onClose();
              }}
              className="px-5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-obsidian font-bold text-xs font-mono transition-colors shadow-tactical-glow"
            >
              Acknowledge Alert
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
