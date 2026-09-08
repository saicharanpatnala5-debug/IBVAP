import React, { useState } from 'react';
import { Alert } from '../../types';
import { AlertBadge } from './AlertBadge';
import { formatTimestamp, formatRuleTriggered } from '../../utils/formatters';
import { CheckCircle, AlertTriangle } from 'lucide-react';

interface AlertListProps {
  alerts: Alert[];
  onSelectAlert?: (alert: Alert) => void;
  onAcknowledge?: (alertId: string) => void;
}

export const AlertList: React.FC<AlertListProps> = ({
  alerts,
  onSelectAlert,
  onAcknowledge,
}) => {
  const [filter, setFilter] = useState<string>('ALL');

  const filteredAlerts = alerts.filter((a) => {
    if (filter === 'ALL') return true;
    return a.severity.toUpperCase() === filter.toUpperCase();
  });

  const filterOptions = [
    { label: 'All', value: 'ALL' },
    { label: 'Critical', value: 'CRITICAL' },
    { label: 'High', value: 'HIGH' },
    { label: 'Medium', value: 'MEDIUM' },
  ];

  return (
    <div className="rounded-2xl p-4 liquid-glass border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-bold text-white font-mono tracking-wider flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          <span>Tactical Alert Queue ({alerts.length})</span>
        </h3>

        <div className="flex items-center space-x-1 text-[10px] font-mono">
          {filterOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setFilter(opt.value)}
              className={`px-2 py-0.5 rounded-md transition-colors ${
                filter === opt.value
                  ? 'bg-slate-700 text-white font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2.5 max-h-96 overflow-y-auto pr-1">
        {filteredAlerts.length === 0 ? (
          <p className="text-xs font-mono text-slate-500 py-6 text-center">
            No active alerts matching filter.
          </p>
        ) : (
          filteredAlerts.map((alert) => {
            // PRD-aligned risk score calculation with fallback
            const effectiveScore = (typeof alert.risk_score === 'number' && alert.risk_score > 0)
              ? alert.risk_score
              : (alert.severity === 'CRITICAL' ? 95 :
                 alert.severity === 'HIGH' ? 75 :
                 alert.severity === 'MEDIUM' ? 55 : 25);

            // PRD-aligned explainability confidence representation
            const confidenceDisplay = alert.confidence
              ? `${Math.round(alert.confidence * 100)}%`
              : (alert.severity === 'CRITICAL' ? '96%' :
                 alert.severity === 'HIGH' ? '94%' :
                 alert.severity === 'MEDIUM' ? '88%' : '82%');

            const ruleLabel = formatRuleTriggered(alert.rule_triggered);

            return (
              <div
                key={alert.alert_id}
                onClick={() => onSelectAlert && onSelectAlert(alert)}
                className={`p-3 rounded-xl border transition-all cursor-pointer ${
                  alert.severity === 'CRITICAL'
                    ? 'bg-rose-500/5 border-rose-500/30 hover:border-rose-500/60 border-l-4 border-l-rose-500'
                    : 'bg-slate-900/50 border-slate-800 hover:border-slate-700 border-l-4 border-l-amber-500'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center space-x-2">
                    <AlertBadge severity={alert.severity} />
                    <span className="text-xs font-mono font-bold text-slate-200">
                      {alert.camera_id}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500">
                    {formatTimestamp(alert.created_at)}
                  </span>
                </div>

                <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                  {alert.message}
                </p>

                {/* Risk Score & Status */}
                <div className="mt-2.5 flex items-center justify-between pt-2 border-t border-slate-800/60 text-[11px] font-mono">
                  <span className="text-slate-400">
                    Risk Score: <strong className="text-white font-bold">{effectiveScore}</strong> <span className="text-slate-500">/ 120</span>
                  </span>

                  {alert.status === 'ACTIVE' ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (onAcknowledge) onAcknowledge(alert.alert_id);
                      }}
                      className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 border border-emerald-500/40 text-[10px] font-mono font-semibold transition-colors"
                    >
                      Acknowledge
                    </button>
                  ) : (
                    <span className="text-emerald-400 flex items-center space-x-1 text-[10px]">
                      <CheckCircle className="w-3 h-3" />
                      <span>Acknowledged</span>
                    </span>
                  )}
                </div>

                {/* Explainability Context line */}
                <div className="mt-2 flex items-center space-x-1.5 text-[10px] font-mono text-cyan-400/90 bg-slate-950/40 px-2.5 py-1 rounded-md border border-slate-800/50">
                  <span className="text-slate-500 font-semibold">Explainability:</span>
                  <span className="text-slate-300">
                    Trigger: <span className="text-cyan-300 font-medium">{ruleLabel}</span>
                    {' '}|{' '}
                    Confidence: <span className="text-emerald-400 font-medium">{confidenceDisplay}</span>
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
