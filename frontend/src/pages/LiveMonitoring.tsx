import React, { useState } from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { CameraGrid } from '../components/camera/CameraGrid';
import { PTZControls } from '../components/camera/PTZControls';
import { LiveStreamPlayer } from '../components/video/LiveStreamPlayer';
import { CCTVUploadModal } from '../components/video/CCTVUploadModal';
import { LiveCCTVConnectModal } from '../components/video/LiveCCTVConnectModal';
import { useCameras } from '../hooks/useCameras';
import { SEOHead } from '../components/common/SEOHead';
import { Camera } from '../types';
import { Radio, UploadCloud, Plus } from 'lucide-react';
import { getDetectionsForTime } from '../utils/detectionEngine';
import { formatSensorType } from '../utils/formatters';

export const LiveMonitoring: React.FC = () => {
  const { cameras } = useCameras();
  const [activeCamId, setActiveCamId] = useState<string>('CAM-01');
  const [customVideoUrl, setCustomVideoUrl] = useState<string | null>(null);
  const [customVideoTitle, setCustomVideoTitle] = useState<string | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false);
  const [isConnectModalOpen, setIsConnectModalOpen] = useState<boolean>(false);

  const selectedCam = cameras.find((c) => c.camera_id === activeCamId) || cameras[0];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto animate-fade-in">
      <SEOHead title="Live Multi-Spectral Surveillance" description="Real-time multi-camera tactical surveillance monitoring" />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <Breadcrumbs
            items={[
              { label: 'Tactical Post' },
              { label: 'Live Monitoring', isCurrent: true },
            ]}
          />
          {customVideoTitle && (
            <div className="flex items-center space-x-2 text-xs font-mono text-cyan-400">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              <span>Playing Ingested Footage: {customVideoTitle} (Looping)</span>
              <button 
                onClick={() => {
                  setCustomVideoUrl(null);
                  setCustomVideoTitle(null);
                }}
                className="text-[10px] text-slate-400 hover:text-white underline ml-1"
              >
                Reset to Live Cam
              </button>
            </div>
          )}
        </div>
        <div className="flex items-center space-x-2.5">
          <button
            onClick={() => setIsConnectModalOpen(true)}
            className="px-3.5 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-obsidian font-mono font-bold text-xs flex items-center space-x-1.5 transition-all shadow-tactical-glow"
          >
            <Radio className="w-3.5 h-3.5" />
            <span>Connect Live Stream</span>
          </button>
          <button
            onClick={() => setIsUploadModalOpen(true)}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-mono text-xs flex items-center space-x-1.5 transition-colors"
          >
            <UploadCloud className="w-3.5 h-3.5 text-cyan-400" />
            <span>Upload CCTV Footage</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main High-Res Tactical Player */}
        <div className="lg:col-span-3 space-y-4">
          {selectedCam && (
            <LiveStreamPlayer 
              camera={selectedCam} 
              customVideoUrl={customVideoUrl || undefined}
              customVideoTitle={customVideoTitle || undefined}
            />
          )}

          {/* Sub-grid of other cameras */}
          <CameraGrid
            cameras={cameras}
            selectedCameraId={activeCamId}
            onSelectCamera={(id) => {
              setActiveCamId(id);
              setCustomVideoUrl(null);
              setCustomVideoTitle(null);
            }}
            onConnectNewCamera={() => setIsConnectModalOpen(true)}
          />
        </div>

        {/* Tactical Controls & Stream Metadata */}
        <div className="space-y-4">
          <PTZControls cameraId={activeCamId} />

          {/* Real-time 4-Class Detection Telemetry Panel */}
          <div className="rounded-2xl p-4 liquid-glass border border-slate-800 text-xs font-mono space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold text-white uppercase flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>Active Targets Telemetry</span>
              </span>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold">
                YOLO26s ONLINE
              </span>
            </div>

            {/* Target Breakdown */}
            {(() => {
              const activeDets = getDetectionsForTime(
                customVideoTitle || customVideoUrl || activeCamId,
                2.0,
                15,
                customVideoTitle || customVideoUrl || selectedCam?.name
              );
              return (
                <div className="space-y-2">
                  {activeDets.map((d) => (
                    <div 
                      key={d.id}
                      className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-white flex items-center space-x-1">
                          <span className={
                            d.class_name === 'person' ? 'text-rose-400' :
                            d.class_name === 'vehicle' ? 'text-cyan-400' :
                            d.class_name === 'object' ? 'text-purple-400' : 'text-amber-400'
                          }>
                            ● {d.track_id}
                          </span>
                          <span className="text-[10px] text-slate-400">[{d.class_name.toUpperCase()}]</span>
                        </span>
                        <span className="text-emerald-400 font-bold text-[11px]">
                          {(d.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="text-[10px] text-slate-300 flex items-center justify-between">
                        <span className="truncate max-w-[150px]">{d.sub_label || d.label}</span>
                        {d.threat_level === 'FILTERED_NON_THREAT' ? (
                          <span className="text-amber-400 font-bold text-[9px]">FILTERED</span>
                        ) : (
                          <span className={d.threat_level === 'CRITICAL' ? 'text-rose-400 font-bold' : 'text-slate-400'}>
                            {d.threat_level}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              );
            })()}
          </div>

          {selectedCam && (
            <div className="rounded-2xl p-4 liquid-glass border border-slate-800 text-xs font-mono space-y-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase">Stream Diagnostics</span>
              <div className="flex justify-between text-slate-300">
                <span className="text-slate-500">RTSP Endpoint:</span>
                <span className="text-cyan-400 truncate max-w-[140px]">{selectedCam.stream_url}</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span className="text-slate-500">Resolution:</span>
                <span className="text-white">{selectedCam.resolution}</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span className="text-slate-500">Sensor:</span>
                <span className="text-emerald-400">{formatSensorType(selectedCam.sensor_type)}</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span className="text-slate-500">Coordinates:</span>
                <span className="text-slate-300">{selectedCam.latitude}, {selectedCam.longitude}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <CCTVUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onFuseToIncident={(inc) => {
          if (inc && inc.videoUrl) {
            setCustomVideoUrl(inc.videoUrl);
            setCustomVideoTitle(inc.title);
          }
        }}
      />

      <LiveCCTVConnectModal
        isOpen={isConnectModalOpen}
        onClose={() => setIsConnectModalOpen(false)}
        onConnectCamera={(cam) => {
          setActiveCamId(cam.camera_id);
        }}
      />
    </div>
  );
};
