import React, { useState } from 'react';
import { Play, Pause, RotateCcw, ShieldCheck, Download } from 'lucide-react';

export const EvidencePlayback: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(42);

  return (
    <div className="rounded-2xl p-4 liquid-glass border border-slate-800">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
        <span className="text-xs font-mono font-bold text-white uppercase">
          FORENSIC EVIDENCE PLAYER [SHA-256 VERIFIED]
        </span>
        <span className="text-[10px] font-mono text-emerald-400 flex items-center space-x-1">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>TAMPER-SEAL INTACT</span>
        </span>
      </div>

      <div className="aspect-video rounded-xl bg-black/80 border border-slate-800 flex items-center justify-center reticle-grid relative">
        <p className="text-xs font-mono text-slate-400">
          PLAYING FORENSIC CLIP: ev_CAM-03_20260906.mp4
        </p>
      </div>

      <div className="mt-4 space-y-2">
        <input
          type="range"
          min={0}
          max={100}
          value={progress}
          onChange={(e) => setProgress(Number(e.target.value))}
          className="w-full accent-emerald-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
        />
        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
          <span>00:14 / 00:35</span>
          <span>1080p @ 25 FPS</span>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between pt-3 border-t border-slate-800">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-2 rounded-lg bg-emerald-500 text-obsidian font-bold hover:bg-emerald-400 transition-colors"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setProgress(0)}
            className="p-2 rounded-lg bg-slate-800 text-slate-300 hover:text-white"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>

        <button className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-200 flex items-center space-x-1.5">
          <Download className="w-3.5 h-3.5 text-cyan-400" />
          <span>Export Sealed MP4</span>
        </button>
      </div>
    </div>
  );
};
