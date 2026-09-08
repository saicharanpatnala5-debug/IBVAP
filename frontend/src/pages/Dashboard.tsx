import React, { useState } from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { BentoGrid } from '../components/common/BentoGrid';
import { CameraGrid } from '../components/camera/CameraGrid';
import { AlertList } from '../components/alerts/AlertList';
import { AlertDetailModal } from '../components/alerts/AlertDetailModal';
import { ThreatRadarChart } from '../components/charts/ThreatRadarChart';
import { HourlyBreachChart } from '../components/charts/HourlyBreachChart';
import { RiskDistributionChart } from '../components/charts/RiskDistributionChart';
import { TacticalMap } from '../components/maps/TacticalMap';
import { useCameras } from '../hooks/useCameras';
import { useAlerts } from '../hooks/useAlerts';
import { Alert, Camera } from '../types';
import { SEOHead } from '../components/common/SEOHead';
import { Activity, Radio, Video, ShieldAlert, Cpu } from 'lucide-react';

interface DashboardProps {
  onNavigate: (page: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const { cameras } = useCameras();
  const { alerts, setAlerts } = useAlerts();
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  const handleAcknowledge = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.alert_id === id ? { ...a, status: 'ACKNOWLEDGED' } : a))
    );
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto animate-fade-in">
      <SEOHead title="Command Post Master Overview" description="Master Tactical Overview for BOP Alpha" />

      <Breadcrumbs items={[{ label: 'Command Post Overview', isCurrent: true }]} />

      {/* Top Telemetry Metric Ribbons */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-2xl p-4 liquid-glass border-l-4 border-emerald-500">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>ONLINE SENSORS</span>
            <Video className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold font-mono text-white mt-2">5 / 5</p>
          <span className="text-[10px] font-mono text-emerald-400">100% Perimeter Coverage</span>
        </div>

        <div className="rounded-2xl p-4 liquid-glass border-l-4 border-rose-500">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>ACTIVE ALERTS</span>
            <ShieldAlert className="w-4 h-4 text-rose-400 animate-pulse" />
          </div>
          <p className="text-2xl font-bold font-mono text-rose-400 mt-2">
            {alerts.filter((a) => a.status === 'ACTIVE').length}
          </p>
          <span className="text-[10px] font-mono text-rose-400">1 High Restricted Zone</span>
        </div>

        <div className="rounded-2xl p-4 liquid-glass border-l-4 border-cyan-500">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>EDGE LATENCY</span>
            <Cpu className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-bold font-mono text-cyan-400 mt-2">14.8 ms</p>
          <span className="text-[10px] font-mono text-cyan-300">Jetson Xavier TensorRT</span>
        </div>

        <div className="rounded-2xl p-4 liquid-glass border-l-4 border-amber-500">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>THREAT LEVEL</span>
            <Radio className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bold font-mono text-amber-400 mt-2">HIGH RISK</p>
          <span className="text-[10px] font-mono text-amber-300">Night Watch Protocol</span>
        </div>
      </div>

      {/* Main Interactive Tactical Map */}
      <TacticalMap />

      {/* Bento Grid Analytics */}
      <BentoGrid />

      {/* Feeds & Alerts Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <CameraGrid
            cameras={cameras.slice(0, 4)}
            onExpandCamera={() => onNavigate('live')}
            onSelectCamera={() => onNavigate('live')}
          />
        </div>
        <div>
          <AlertList
            alerts={alerts}
            onSelectAlert={(a) => setSelectedAlert(a)}
            onAcknowledge={handleAcknowledge}
          />
        </div>
      </div>

      {/* Analytical Charts */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ThreatRadarChart />
        <HourlyBreachChart />
        <RiskDistributionChart />
      </div>

      <AlertDetailModal
        alert={selectedAlert}
        onClose={() => setSelectedAlert(null)}
        onAcknowledge={handleAcknowledge}
      />
    </div>
  );
};
