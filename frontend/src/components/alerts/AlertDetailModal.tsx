import React from 'react';
import { Alert } from '../../types';
import { AlertBadge } from './AlertBadge';
import { formatTimestamp } from '../../utils/formatters';
import { X, Radio } from 'lucide-react';

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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div className="relative w-full max-w-2xl rounded-3xl p-6 liquid-glass border border-slate-700 shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <AlertBadge severity={alert.severity} />
            <h3 className="text-base font-bold text-white font-mono">
              {alert.alert_id} — TACTICAL INCIDENT
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="my-4 relative aspect-video rounded-2xl bg-black border border-slate-800 overflow-hidden flex items-center justify-center reticle-grid">
          <div className="text-center p-4">
            <Radio className="w-8 h-8 text-rose-500 mx-auto mb-2 animate-pulse" />
            <p className="text-xs font-mono text-slate-400">
              TACTICAL EVIDENCE SNAPSHOT [{alert.camera_id}]
            </p>
            <p className="text-[10px] font-mono text-slate-500 mt-1">
              RULE: {alert.rule_triggered}
            </p>
          </div>

          <div className="absolute top-4 left-4 w-4 h-4 border-t-2 border-l-2 border-rose-500" />
          <div className="absolute top-4 right-4 w-4 h-4 border-t-2 border-r-2 border-rose-500" />
          <div className="absolute bottom-4 left-4 w-4 h-4 border-b-2 border-l-2 border-rose-500" />
          <div className="absolute bottom-4 right-4 w-4 h-4 border-b-2 border-r-2 border-rose-500" />
        </div>

        <div className="grid grid-cols-2 gap-4 text-xs font-mono py-2">
          <div>
            <span className="text-slate-500 block">TIMESTAMP</span>
            <span className="text-slate-200">{formatTimestamp(alert.created_at)}</span>
          </div>
          <div>
            <span className="text-slate-500 block">RISK SCORE</span>
            <span className="text-emerald-400 font-bold">{alert.risk_score} / 120</span>
          </div>
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
              Acknowledge & Dispatch QRT
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
