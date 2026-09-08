import React, { useState } from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { CameraGrid } from '../components/camera/CameraGrid';
import { PTZControls } from '../components/camera/PTZControls';
import { LiveStreamPlayer } from '../components/video/LiveStreamPlayer';
import { useCameras } from '../hooks/useCameras';
import { SEOHead } from '../components/common/SEOHead';
import { Camera } from '../types';

export const LiveMonitoring: React.FC = () => {
  const { cameras } = useCameras();
  const [activeCamId, setActiveCamId] = useState<string>('CAM-01');

  const selectedCam = cameras.find((c) => c.camera_id === activeCamId) || cameras[0];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto animate-fade-in">
      <SEOHead title="Live Multi-Spectral Surveillance" description="Real-time multi-camera tactical surveillance monitoring" />

      <Breadcrumbs
        items={[
          { label: 'Tactical Post' },
          { label: 'Live Monitoring', isCurrent: true },
        ]}
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main High-Res Tactical Player */}
        <div className="lg:col-span-3 space-y-4">
          {selectedCam && <LiveStreamPlayer camera={selectedCam} />}

          {/* Sub-grid of other cameras */}
          <CameraGrid
            cameras={cameras}
            selectedCameraId={activeCamId}
            onSelectCamera={(id) => setActiveCamId(id)}
          />
        </div>

        {/* Tactical Controls & Stream Metadata */}
        <div className="space-y-4">
          <PTZControls cameraId={activeCamId} />

          {selectedCam && (
            <div className="rounded-2xl p-4 liquid-glass border border-slate-800 text-xs font-mono space-y-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase">Stream Diagnostics</span>
              <div className="flex justify-between text-slate-300">
                <span>RTSP ENDPOINT:</span>
                <span className="text-cyan-400 truncate max-w-[140px]">{selectedCam.stream_url}</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>RESOLUTION:</span>
                <span className="text-white">{selectedCam.resolution}</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>SENSOR:</span>
                <span className="text-emerald-400">{selectedCam.sensor_type || 'OPTICAL_4K'}</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>LAT/LON:</span>
                <span className="text-slate-300">{selectedCam.latitude}, {selectedCam.longitude}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
