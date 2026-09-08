import React from 'react';
import { Camera, CameraStatus } from '../../types';
import { Video, Maximize2 } from 'lucide-react';

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
          <span className="text-[10px] font-mono text-slate-400">{camera.sensor_type || 'OPTICAL_4K'}</span>
        </div>
        <span
          className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded border uppercase ${getStatusBadge(
            camera.status
          )}`}
        >
          {camera.status}
        </span>
      </div>

      <div className="relative aspect-video rounded-xl bg-black/60 border border-slate-800 overflow-hidden flex items-center justify-center reticle-grid">
        <div className="absolute inset-0 flex flex-col items-center justify-center opacity-40">
          <Video className="w-8 h-8 text-emerald-400 mb-1 animate-pulse" />
          <span className="text-[10px] font-mono text-slate-400">{camera.name}</span>
        </div>

        <div className="absolute top-2 left-2 w-3 h-3 border-t-2 border-l-2 border-emerald-500/60" />
        <div className="absolute top-2 right-2 w-3 h-3 border-t-2 border-r-2 border-emerald-500/60" />
        <div className="absolute bottom-2 left-2 w-3 h-3 border-b-2 border-l-2 border-emerald-500/60" />
        <div className="absolute bottom-2 right-2 w-3 h-3 border-b-2 border-r-2 border-emerald-500/60" />

        <div className="absolute bottom-2 left-2 text-[9px] font-mono text-emerald-400 bg-black/70 px-1 rounded">
          {camera.fps.toFixed(1)} FPS
        </div>
        <div className="absolute top-2 right-2 text-[9px] font-mono text-slate-400 bg-black/70 px-1 rounded">
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
