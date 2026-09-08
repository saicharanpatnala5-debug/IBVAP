import React from 'react';

interface HUDOverlayProps {
  cameraName?: string;
  fps?: number;
  coordinates?: string;
}

export const HUDOverlay: React.FC<HUDOverlayProps> = ({
  cameraName = 'BOP-CAM-01',
  fps = 25.0,
  coordinates = '28.6139° N, 77.2090° E',
}) => {
  return (
    <div className="absolute inset-0 pointer-events-none p-4 flex flex-col justify-between text-[10px] font-mono text-emerald-400">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2 bg-black/60 px-2 py-1 rounded backdrop-blur-sm border border-emerald-500/20">
          <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
          <span className="font-bold text-white">LIVE REC</span>
          <span>[{cameraName}]</span>
        </div>
        <div className="bg-black/60 px-2 py-1 rounded backdrop-blur-sm border border-emerald-500/20">
          <span>{fps.toFixed(1)} FPS | 3840x2160</span>
        </div>
      </div>

      <div className="self-center my-auto relative w-24 h-24 flex items-center justify-center">
        <div className="w-16 h-16 rounded-full border border-emerald-500/40 border-dashed" />
        <div className="absolute w-2 h-2 bg-emerald-400 rounded-full opacity-60" />
        <div className="absolute top-0 w-0.5 h-3 bg-emerald-400/60" />
        <div className="absolute bottom-0 w-0.5 h-3 bg-emerald-400/60" />
        <div className="absolute left-0 h-0.5 w-3 bg-emerald-400/60" />
        <div className="absolute right-0 h-0.5 w-3 bg-emerald-400/60" />
      </div>

      <div className="flex items-center justify-between">
        <div className="bg-black/60 px-2 py-1 rounded backdrop-blur-sm border border-emerald-500/20">
          <span>COORDS: {coordinates}</span>
        </div>
        <div className="bg-black/60 px-2 py-1 rounded backdrop-blur-sm border border-emerald-500/20">
          <span>BEARING: 042° NE</span>
        </div>
      </div>
    </div>
  );
};
