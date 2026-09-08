import React, { useState } from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { AlertList } from '../components/alerts/AlertList';
import { AlertDetailModal } from '../components/alerts/AlertDetailModal';
import { useAlerts } from '../hooks/useAlerts';
import { SEOHead } from '../components/common/SEOHead';
import { Alert } from '../types';
import { Bell, CheckCheck, Download } from 'lucide-react';

export const Alerts: React.FC = () => {
  const { alerts, setAlerts } = useAlerts();
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  const handleAcknowledge = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.alert_id === id ? { ...a, status: 'ACKNOWLEDGED' } : a))
    );
  };

  const handleAckAll = () => {
    setAlerts((prev) => prev.map((a) => ({ ...a, status: 'ACKNOWLEDGED' })));
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto animate-fade-in">
      <SEOHead title="Tactical Alerts Triage" description="Frontline threat alert management and response" />

      <div className="flex items-center justify-between">
        <Breadcrumbs items={[{ label: 'Tactical Alerts Triage', isCurrent: true }]} />
        <div className="flex items-center space-x-3">
          <button
            onClick={handleAckAll}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-200 flex items-center space-x-1.5"
          >
            <CheckCheck className="w-4 h-4 text-emerald-400" />
            <span>Acknowledge All</span>
          </button>
          <button className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-200 flex items-center space-x-1.5">
            <Download className="w-4 h-4 text-cyan-400" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      <AlertList
        alerts={alerts}
        onSelectAlert={(a) => setSelectedAlert(a)}
        onAcknowledge={handleAcknowledge}
      />

      <AlertDetailModal
        alert={selectedAlert}
        onClose={() => setSelectedAlert(null)}
        onAcknowledge={handleAcknowledge}
      />
    </div>
  );
};
