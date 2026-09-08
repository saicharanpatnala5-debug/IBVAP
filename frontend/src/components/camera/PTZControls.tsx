import React, { useState } from 'react';
import { 
  ChevronUp, ChevronDown, ChevronLeft, ChevronRight, 
  ZoomIn, ZoomOut, RotateCcw, Compass 
} from 'lucide-react';

interface PTZControlsProps {
  cameraId?: string;
}

export const PTZControls: React.FC<PTZControlsProps> = ({ cameraId = 'CAM-01' }) => {
  const [activeAction, setActiveAction] = useState<string>('IDLE');

  const trigger = (action: string) => {
    setActiveAction(action);
    setTimeout(() => setActiveAction('IDLE'), 800);
  };

  const presets = ['North Fence', 'Sector Gate', 'Observation Ridge', 'Inner Armory'];

  return (
    <div className="rounded-2xl p-4 liquid-glass border border-slate-800">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
        <span className="text-xs font-bold text-white font-mono flex items-center space-x-1.5">
          <Compass className="w-3.5 h-3.5 text-cyan-400" />
          <span>PTZ CONTROLS [{cameraId}]</span>
        </span>
        <span className="text-[10px] font-mono text-emerald-400 uppercase font-semibold">
          {activeAction}
        </span>
      </div>

      <div className="flex flex-col items-center justify-center my-3">
        <button
          onClick={() => trigger('TILT UP')}
          className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 active:bg-emerald-500 active:text-obsidian transition-colors mb-1"
        >
          <ChevronUp className="w-4 h-4" />
        </button>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => trigger('PAN LEFT')}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 active:bg-emerald-500 active:text-obsidian transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => trigger('RECENTER')}
            className="p-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-400 hover:text-white"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => trigger('PAN RIGHT')}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 active:bg-emerald-500 active:text-obsidian transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
        <button
          onClick={() => trigger('TILT DOWN')}
          className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 active:bg-emerald-500 active:text-obsidian transition-colors mt-1"
        >
          <ChevronDown className="w-4 h-4" />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-slate-800">
        <button
          onClick={() => trigger('ZOOM IN')}
          className="py-2 px-3 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-xs font-mono text-slate-200 flex items-center justify-center space-x-1"
        >
          <ZoomIn className="w-3.5 h-3.5 text-cyan-400" />
          <span>Zoom +</span>
        </button>
        <button
          onClick={() => trigger('ZOOM OUT')}
          className="py-2 px-3 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-xs font-mono text-slate-200 flex items-center justify-center space-x-1"
        >
          <ZoomOut className="w-3.5 h-3.5 text-cyan-400" />
          <span>Zoom -</span>
        </button>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800">
        <p className="text-[10px] font-mono text-slate-400 uppercase mb-2">Tactical Presets</p>
        <div className="grid grid-cols-2 gap-1.5">
          {presets.map((p, idx) => (
            <button
              key={idx}
              onClick={() => trigger(`PRESET: ${p.toUpperCase()}`)}
              className="px-2 py-1.5 rounded-lg bg-slate-900/60 hover:bg-slate-800 border border-slate-800 text-[10px] font-mono text-slate-300 text-left truncate"
            >
              #{idx + 1} {p}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
