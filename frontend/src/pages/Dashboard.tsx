import React, { useState } from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { CameraGrid } from '../components/camera/CameraGrid';
import { AlertList } from '../components/alerts/AlertList';
import { AlertDetailModal } from '../components/alerts/AlertDetailModal';
import { ThreatRadarChart } from '../components/charts/ThreatRadarChart';
import { HourlyBreachChart } from '../components/charts/HourlyBreachChart';
import { RiskDistributionChart } from '../components/charts/RiskDistributionChart';
import { TacticalMap } from '../components/maps/TacticalMap';
import { TacticalIngestionHub } from '../components/video/TacticalIngestionHub';
import { CCTVUploadModal } from '../components/video/CCTVUploadModal';
import { LiveCCTVConnectModal } from '../components/video/LiveCCTVConnectModal';
import { useCameras } from '../hooks/useCameras';
import { useAlerts } from '../hooks/useAlerts';
import { useTacticalStore } from '../store/useTacticalStore';
import { getSeverityBadgeStyles } from '../utils/formatters';
import { Alert, Camera } from '../types';
import { SEOHead } from '../components/common/SEOHead';
import { Activity, Radio, Video, ShieldAlert, Cpu, UploadCloud, Plus } from 'lucide-react';

interface DashboardProps {
  onNavigate: (page: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const { cameras } = useCameras();
  const { alerts, setAlerts } = useAlerts();
  const { threatLevel } = useTacticalStore();
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false);
  const [isConnectModalOpen, setIsConnectModalOpen] = useState<boolean>(false);
  const [hubVideo, setHubVideo] = useState<{ url?: string; title?: string }>({});

  const activeAlertsCount = alerts.filter((a) => a.status === 'ACTIVE' || !a.is_acknowledged).length;
  const threatStyles = getSeverityBadgeStyles(threatLevel);
  const threatBorderColor =
    threatLevel === 'CRITICAL' ? 'border-rose-500' :
    threatLevel === 'HIGH' ? 'border-orange-500' :
    threatLevel === 'MEDIUM' ? 'border-amber-500' :
    threatLevel === 'LOW' ? 'border-blue-500' : 'border-emerald-500';
  const formattedThreatLevel = threatLevel.charAt(0) + threatLevel.slice(1).toLowerCase();

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
            <span>Online Sensors</span>
            <Video className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold font-mono text-white mt-2">
            {cameras.length > 0 ? `${cameras.filter(c => c.status === 'ONLINE').length || cameras.length} / ${cameras.length}` : '5 / 5'}
          </p>
          <span className="text-[10px] font-mono text-emerald-400">100% Perimeter Coverage</span>
        </div>

        <div className="rounded-2xl p-4 liquid-glass border-l-4 border-rose-500">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>Active Alerts</span>
            <ShieldAlert className={`w-4 h-4 ${activeAlertsCount > 0 ? 'text-rose-400 animate-pulse' : 'text-slate-500'}`} />
          </div>
          <p className="text-2xl font-bold font-mono text-rose-400 mt-2">
            {activeAlertsCount}
          </p>
          <span className="text-[10px] font-mono text-rose-400">
            {activeAlertsCount > 0 ? `${activeAlertsCount} Active Incident${activeAlertsCount > 1 ? 's' : ''}` : 'All Zones Secure'}
          </span>
        </div>

        <div className="rounded-2xl p-4 liquid-glass border-l-4 border-cyan-500">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>Edge Latency</span>
            <Cpu className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-bold font-mono text-cyan-400 mt-2">14.8 ms</p>
          <span className="text-[10px] font-mono text-cyan-300">Jetson Xavier TensorRT</span>
        </div>

        <div className={`rounded-2xl p-4 liquid-glass border-l-4 ${threatBorderColor}`}>
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>Threat Level</span>
            <Radio className={`w-4 h-4 ${threatStyles.text}`} />
          </div>
          <p className={`text-2xl font-bold font-mono mt-2 ${threatStyles.text}`}>
            {formattedThreatLevel}
          </p>
          <span className="text-[10px] font-mono text-slate-400">Night Watch Protocol</span>
        </div>
      </div>

      {/* Main Interactive Tactical Map */}
      <TacticalMap alerts={alerts} />

      {/* Tactical Video Ingestion & Live Streams Hub */}
      <TacticalIngestionHub
        onOpenUploadModal={(url, title) => {
          setHubVideo({ url, title });
          setIsUploadModalOpen(true);
        }}
        onOpenConnectModal={() => setIsConnectModalOpen(true)}
        onSelectCamera={(id) => onNavigate('live')}
      />

      {/* Feeds & Alerts Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <CameraGrid
            cameras={cameras.slice(0, 4)}
            onExpandCamera={() => onNavigate('live')}
            onSelectCamera={() => onNavigate('live')}
            onConnectNewCamera={() => setIsConnectModalOpen(true)}
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

      {/* Forensic CCTV Footage Upload Modal */}
      <CCTVUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        initialVideoUrl={hubVideo.url}
        initialVideoTitle={hubVideo.title}
        onFuseToIncident={(inc) => {
          onNavigate('incidents');
        }}
      />

      {/* Live CCTV Stream Connect Modal */}
      <LiveCCTVConnectModal
        isOpen={isConnectModalOpen}
        onClose={() => setIsConnectModalOpen(false)}
        onConnectCamera={(newCam) => {
          onNavigate('live');
        }}
      />
    </div>
  );
};
