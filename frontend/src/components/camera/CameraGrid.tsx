import React, { useState } from 'react';
import { Camera } from '../../types';
import { CameraCard } from './CameraCard';
import { Grid2X2, Grid3X3, Maximize, Plus, Radio } from 'lucide-react';

interface CameraGridProps {
  cameras: Camera[];
  selectedCameraId?: string;
  onSelectCamera?: (camId: string) => void;
  onExpandCamera?: (cam: Camera) => void;
  onConnectNewCamera?: () => void;
}

export const CameraGrid: React.FC<CameraGridProps> = ({
  cameras,
  selectedCameraId,
  onSelectCamera,
  onExpandCamera,
  onConnectNewCamera,
}) => {
  const [layout, setLayout] = useState<'2x2' | '3x2' | 'single'>('2x2');

  const getGridClass = () => {
    switch (layout) {
      case 'single':
        return 'grid-cols-1';
      case '3x2':
        return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3';
      case '2x2':
      default:
        return 'grid-cols-1 md:grid-cols-2';
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-mono text-slate-400">
          ACTIVE SURVEILLANCE FEEDS ({cameras.length})
        </span>
        <div className="flex items-center space-x-1.5 bg-slate-900/60 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setLayout('single')}
            className={`p-1.5 rounded-lg text-xs font-mono transition-colors ${
              layout === 'single' ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-400'
            }`}
          >
            <Maximize className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setLayout('2x2')}
            className={`p-1.5 rounded-lg text-xs font-mono transition-colors ${
              layout === '2x2' ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-400'
            }`}
          >
            <Grid2X2 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setLayout('3x2')}
            className={`p-1.5 rounded-lg text-xs font-mono transition-colors ${
              layout === '3x2' ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-400'
            }`}
          >
            <Grid3X3 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div className={`grid ${getGridClass()} gap-4`}>
        {cameras.map((cam) => (
          <CameraCard
            key={cam.camera_id}
            camera={cam}
            isSelected={selectedCameraId === cam.camera_id}
            onSelect={() => onSelectCamera && onSelectCamera(cam.camera_id)}
            onExpand={() => onExpandCamera && onExpandCamera(cam)}
          />
        ))}

        {onConnectNewCamera && (
          <div
            onClick={onConnectNewCamera}
            className="rounded-2xl p-4 border-2 border-dashed border-slate-800 hover:border-emerald-500/60 bg-slate-900/30 flex flex-col items-center justify-center text-center cursor-pointer transition-all hover:bg-slate-900/60 group aspect-video min-h-[160px]"
          >
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform mb-2">
              <Plus className="w-5 h-5" />
            </div>
            <span className="text-xs font-mono font-bold text-white group-hover:text-emerald-400 transition-colors">
              Connect Live CCTV
            </span>
            <span className="text-[10px] font-mono text-slate-400 mt-1">
              Add RTSP / HLS / IP Camera Feed
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
