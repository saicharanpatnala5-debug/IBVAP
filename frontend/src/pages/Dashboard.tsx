import React, { useState, useRef } from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { CameraGrid } from '../components/camera/CameraGrid';
import { LiveStreamPlayer } from '../components/video/LiveStreamPlayer';
import { AlertList } from '../components/alerts/AlertList';
import { AlertDetailModal } from '../components/alerts/AlertDetailModal';
import { ThreatRadarChart } from '../components/charts/ThreatRadarChart';
import { HourlyBreachChart } from '../components/charts/HourlyBreachChart';
import { RiskDistributionChart } from '../components/charts/RiskDistributionChart';
import { CCTVUploadModal } from '../components/video/CCTVUploadModal';
import { LiveCCTVConnectModal } from '../components/video/LiveCCTVConnectModal';
import { useCameras } from '../hooks/useCameras';
import { useAlerts } from '../hooks/useAlerts';
import { Alert, Camera } from '../types';
import { SEOHead } from '../components/common/SEOHead';
import { registerVideoBlob } from '../utils/detectionEngine';
import { Video, ShieldAlert, UploadCloud, Radio } from 'lucide-react';

interface DashboardProps {
  onNavigate: (page: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const { cameras } = useCameras();
  const { alerts, setAlerts } = useAlerts();
  const [activeCamId, setActiveCamId] = useState<string>('CAM-01');
  const [activeVideoUrl, setActiveVideoUrl] = useState<string | null>(null);
  const [activeVideoTitle, setActiveVideoTitle] = useState<string | null>(null);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false);
  const [isConnectModalOpen, setIsConnectModalOpen] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Dynamic metrics
  const activeAlertsCount = alerts.length;
  const onlineCamerasCount = cameras.filter((c) => c.status === 'ONLINE').length || cameras.length;
  const selectedCam = cameras.find((c) => c.camera_id === activeCamId) || cameras[0];

  const handleAcknowledge = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.alert_id === id ? { ...a, status: 'ACKNOWLEDGED' } : a))
    );
  };

  const handleFileIngest = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (activeVideoUrl && activeVideoUrl.startsWith('blob:')) {
        try {
          URL.revokeObjectURL(activeVideoUrl);
        } catch {
          // ignore
        }
      }
      const url = URL.createObjectURL(file);
      registerVideoBlob(url, file.name);
      setActiveVideoUrl(url);
      setActiveVideoTitle(file.name);
    }
  };

  const handleResetToLiveCam = () => {
    if (activeVideoUrl && activeVideoUrl.startsWith('blob:')) {
      try {
        URL.revokeObjectURL(activeVideoUrl);
      } catch {
        // ignore
      }
    }
    setActiveVideoUrl(null);
    setActiveVideoTitle(null);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto animate-fade-in">
      <SEOHead title="Command Post Master Overview" description="Master Tactical Overview for BOP Alpha" />

      <Breadcrumbs items={[{ label: 'Command Post Overview', isCurrent: true }]} />

      {/* Top Telemetry Metric Ribbons - Dynamically Wired */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="rounded-2xl p-4 liquid-glass border-l-4 border-emerald-500">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>Online Sensors</span>
            <Video className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold font-mono text-white mt-2">
            {cameras.length > 0 ? `${onlineCamerasCount} / ${cameras.length}` : '5 / 5'}
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
            {activeAlertsCount > 0 ? `${activeAlertsCount} Active Threat Event${activeAlertsCount > 1 ? 's' : ''}` : 'All Zones Secure'}
          </span>
        </div>
      </div>

      {/* Live Camera Surveillance Grid & Threat Queue (PRD Section 15.1) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Main Live Camera Surveillance Grid & Active Video Feed */}
        <div className="lg:col-span-2 space-y-4">
          {/* Active Video Feed Player / Ingested CCTV Perception Feed */}
          <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4 space-y-3 shadow-tactical">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
              <div className="flex items-center space-x-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
                <h3 className="text-xs font-bold font-mono text-white tracking-wider uppercase flex items-center space-x-2">
                  <span>Live Camera Feed & AI Perception</span>
                  {activeVideoTitle ? (
                    <span className="text-[10px] font-normal px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                      Footage: {activeVideoTitle}
                    </span>
                  ) : selectedCam ? (
                    <span className="text-[10px] font-normal px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      Channel: {selectedCam.camera_id} ({selectedCam.name})
                    </span>
                  ) : null}
                </h3>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileIngest}
                  accept="video/mp4,video/avi,video/mkv,video/webm,video/*"
                  className="hidden"
                />
                {activeVideoUrl && (
                  <button
                    onClick={handleResetToLiveCam}
                    className="px-2.5 py-1 rounded-lg text-[10px] font-mono text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors cursor-pointer"
                  >
                    Reset to Live Cam
                  </button>
                )}
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-2.5 py-1 rounded-lg text-[10px] font-mono text-slate-200 bg-slate-800 hover:bg-slate-700 border border-slate-700 flex items-center space-x-1 transition-colors cursor-pointer"
                  title="Upload CCTV footage file"
                >
                  <UploadCloud className="w-3 h-3 text-cyan-400" />
                  <span>Upload CCTV</span>
                </button>
                <button
                  onClick={() => setIsConnectModalOpen(true)}
                  className="px-2.5 py-1 rounded-lg text-[10px] font-mono text-emerald-300 bg-emerald-950/60 hover:bg-emerald-900/60 border border-emerald-500/40 flex items-center space-x-1 transition-colors cursor-pointer"
                  title="Link live RTSP stream"
                >
                  <Radio className="w-3 h-3 text-emerald-400" />
                  <span>Link RTSP</span>
                </button>
              </div>
            </div>

            {/* Video Viewport: Active Stream or Clean Ready State */}
            {selectedCam ? (
              <div className="relative rounded-xl overflow-hidden aspect-video bg-black border border-slate-800/80">
                <LiveStreamPlayer
                  camera={selectedCam}
                  customVideoUrl={activeVideoUrl || undefined}
                  customVideoTitle={activeVideoTitle || undefined}
                />
              </div>
            ) : (
              <div className="rounded-xl border-2 border-dashed border-slate-800 p-10 text-center flex flex-col items-center justify-center bg-slate-900/30 aspect-video">
                <Video className="w-12 h-12 text-slate-600 mb-3" />
                <p className="text-sm font-mono text-slate-300 font-bold">Ready for CCTV Ingestion</p>
                <p className="text-xs font-mono text-slate-500 mt-1 max-w-sm">
                  Upload recorded CCTV video footage or link an RTSP stream to initialize multi-class inference.
                </p>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="mt-4 px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-obsidian font-mono font-bold text-xs cursor-pointer"
                >
                  Upload CCTV File
                </button>
              </div>
            )}
          </div>

          {/* Sub-grid of Active Camera Fleet */}
          <CameraGrid
            cameras={cameras}
            selectedCameraId={activeCamId}
            onSelectCamera={(id) => {
              setActiveCamId(id);
              if (activeVideoUrl && activeVideoUrl.startsWith('blob:')) {
                try {
                  URL.revokeObjectURL(activeVideoUrl);
                } catch {
                  // ignore
                }
              }
              setActiveVideoUrl(null);
              setActiveVideoTitle(null);
            }}
            onExpandCamera={() => onNavigate('live')}
            onConnectNewCamera={() => setIsConnectModalOpen(true)}
          />
        </div>

        {/* Right Col: Tactical Alerts Queue */}
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

      {/* Alert Detail Modal */}
      <AlertDetailModal
        alert={selectedAlert}
        onClose={() => setSelectedAlert(null)}
        onAcknowledge={handleAcknowledge}
      />

      {/* Forensic CCTV Footage Upload Modal */}
      <CCTVUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        initialVideoUrl={activeVideoUrl || undefined}
        initialVideoTitle={activeVideoTitle || undefined}
        onFuseToIncident={() => {
          onNavigate('alerts');
        }}
      />

      {/* Live CCTV Stream Connect Modal */}
      <LiveCCTVConnectModal
        isOpen={isConnectModalOpen}
        onClose={() => setIsConnectModalOpen(false)}
        onConnectCamera={() => {
          onNavigate('live');
        }}
      />
    </div>
  );
};
