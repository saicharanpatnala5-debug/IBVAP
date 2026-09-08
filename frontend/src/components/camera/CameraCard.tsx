import React from 'react';
import { Camera, CameraStatus } from '../../types';
import { Video, Maximize2, User, Car, Sparkles, Crosshair } from 'lucide-react';
import { getCameraVideoUrl } from '../../utils/videoFeeds';
import { getDetectionsForTime, computeTelemetry } from '../../utils/detectionEngine';
import { formatSensorType } from '../../utils/formatters';

interface CameraCardProps {
  camera: Camera;
  isSelected?: boolean;
  onSelect?: () => void;
  onExpand?: () => void;
}

export const CameraCard: React.FC<CameraCardProps> = ({
  camera,
  isSelected,
  onSelect,
  onExpand,
}) => {
  const telemetry = computeTelemetry(getDetectionsForTime(camera.camera_id, 3.0, 15));

  const getStatusBadge = (status: CameraStatus) => {
    switch (status) {
      case 'ONLINE':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
      case 'DEGRADED':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      case 'OFFLINE':
      default:
        return 'bg-rose-500/20 text-rose-400 border-rose-500/40';
    }
  };

  const getBorderColor = (status: CameraStatus) => {
    switch (status) {
      case 'ONLINE':
        return 'border-l-4 border-emerald-500';
      case 'DEGRADED':
        return 'border-l-4 border-amber-500';
      case 'OFFLINE':
      default:
        return 'border-l-4 border-rose-500';
    }
  };

  const formattedStatus = camera.status.charAt(0) + camera.status.slice(1).toLowerCase();

  return (
    <div
      onClick={onSelect}
      className={`rounded-2xl p-4 liquid-glass cursor-pointer transition-all duration-300 ${getBorderColor(
        camera.status
      )} ${
        isSelected
          ? 'ring-2 ring-emerald-500 shadow-tactical-glow bg-slate-900/90'
          : 'hover:border-slate-700'
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="font-mono text-xs font-bold text-white">{camera.camera_id}</span>
          <span className="text-[10px] font-mono text-slate-400">{formatSensorType(camera.sensor_type)}</span>
        </div>
        <div className="flex items-center space-x-1.5">
          {/* Live 4-Class Target Indicators */}
          <div className="flex items-center space-x-1.5 bg-black/60 px-1.5 py-0.5 rounded border border-slate-800 text-[9px] font-mono">
            <span className={telemetry.personCount > 0 ? "text-rose-400 font-bold" : "text-slate-600"} title="Person Targets">P:{telemetry.personCount}</span>
            <span className={telemetry.vehicleCount > 0 ? "text-cyan-400 font-bold" : "text-slate-600"} title="Vehicle Targets">V:{telemetry.vehicleCount}</span>
            <span className={telemetry.objectCount > 0 ? "text-purple-400 font-bold" : "text-slate-600"} title="Objects & Weapons">O:{telemetry.objectCount}</span>
            <span className={telemetry.animalCount > 0 ? "text-amber-400 font-bold" : "text-slate-600"} title="Animals (Filtered)">A:{telemetry.animalCount}</span>
          </div>
          <span
            className={`text-[9px] font-mono font-semibold px-2 py-0.5 rounded border ${getStatusBadge(
              camera.status
            )}`}
          >
            {formattedStatus}
          </span>
        </div>
      </div>

      <div className="relative aspect-video rounded-xl bg-black border border-slate-800 overflow-hidden flex items-center justify-center group">
        <video
          src={getCameraVideoUrl(camera.camera_id, camera.stream_url)}
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />

        <div className="absolute top-2 left-2 w-3 h-3 border-t-2 border-l-2 border-emerald-500/60 pointer-events-none" />
        <div className="absolute top-2 right-2 w-3 h-3 border-t-2 border-r-2 border-emerald-500/60 pointer-events-none" />
        <div className="absolute bottom-2 left-2 w-3 h-3 border-b-2 border-l-2 border-emerald-500/60 pointer-events-none" />
        <div className="absolute bottom-2 right-2 w-3 h-3 border-b-2 border-r-2 border-emerald-500/60 pointer-events-none" />

        <div className="absolute top-2 left-2 flex items-center space-x-1 bg-black/70 backdrop-blur-sm px-1.5 py-0.5 rounded text-[9px] font-mono text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping" />
          <span>LIVE</span>
        </div>

        <div className="absolute bottom-2 left-2 text-[9px] font-mono text-emerald-400 bg-black/70 px-1 rounded backdrop-blur-sm">
          {camera.fps.toFixed(1)} FPS
        </div>
        <div className="absolute top-2 right-2 text-[9px] font-mono text-slate-300 bg-black/70 px-1 rounded backdrop-blur-sm">
          {camera.resolution}
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between text-xs font-mono text-slate-400">
        <span className="truncate pr-2">{camera.site} — {camera.sector}</span>
        {onExpand && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onExpand();
            }}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </div>
  );
};
