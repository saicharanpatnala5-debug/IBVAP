import React from 'react';
import { ShieldCheck, Eye, AlertOctagon } from 'lucide-react';

export const BentoGrid: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-7xl mx-auto my-6">
      <div className="md:col-span-2 rounded-2xl p-6 liquid-glass border border-slate-800/80 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-mono uppercase tracking-widest px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold">
              EDGE SURVEILLANCE ENGINE
            </span>
            <span className="text-xs font-mono text-slate-400">SIH26187 AI Node</span>
          </div>
          <h3 className="text-xl font-bold text-white mb-2">Real-Time Multi-Spectral Edge Analytics</h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            Direct ingestion of RTSP streams with concurrent optical 4K and thermal LWIR processing. Retinex illumination enhancement normalizes night feeds before YOLOv8 tensor inference.
          </p>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-slate-800">
          <div>
            <p className="text-[10px] font-mono text-slate-400">INFERENCE LATENCY</p>
            <p className="text-lg font-bold font-mono text-emerald-400">14.8 ms</p>
          </div>
          <div>
            <p className="text-[10px] font-mono text-slate-400">CONFIRMATION FRAMES</p>
            <p className="text-lg font-bold font-mono text-cyan-400">3 Frames</p>
          </div>
          <div>
            <p className="text-[10px] font-mono text-slate-400">FALSE ALARM DROP</p>
            <p className="text-lg font-bold font-mono text-emerald-400">92.4%</p>
          </div>
        </div>
      </div>

      <div className="rounded-2xl p-6 liquid-glass border-l-4 border-rose-500 flex flex-col justify-between">
        <div>
          <div className="flex items-center space-x-2 text-rose-400 mb-2">
            <AlertOctagon className="w-4 h-4 animate-pulse" />
            <span className="text-[10px] font-mono uppercase font-bold tracking-widest">ZERO TOLERANCE LINE</span>
          </div>
          <h4 className="text-sm font-bold text-white mb-1">Sector B Fence Line</h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Virtual ray-casting polygonal barrier. Instant critical alert dispatched upon boundary traversal.
          </p>
        </div>

        <div className="mt-4 p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-mono">
          <div className="flex items-center justify-between">
            <span>GRID: 28.6152N, 77.2081E</span>
            <span className="font-bold">ARMED</span>
          </div>
        </div>
      </div>

      <div className="rounded-2xl p-6 liquid-glass border border-slate-800 flex flex-col justify-between">
        <div>
          <div className="flex items-center space-x-2 text-cyan-400 mb-2">
            <Eye className="w-4 h-4" />
            <span className="text-[10px] font-mono uppercase font-bold tracking-widest">BIOMETRIC ENGINE</span>
          </div>
          <h4 className="text-sm font-bold text-white mb-1">YuNet & SFace Sighting</h4>
          <p className="text-xs text-slate-400">Cos-similarity matching against National Terrorist Watchlist.</p>
        </div>
        <div className="mt-4 flex items-center justify-between text-xs font-mono text-slate-300">
          <span>MATCH THRESHOLD:</span>
          <span className="text-cyan-400 font-bold">0.82 COSINE</span>
        </div>
      </div>

      <div className="md:col-span-2 rounded-2xl p-6 liquid-glass border border-slate-800 flex flex-col justify-between">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2 text-emerald-400">
            <ShieldCheck className="w-4 h-4" />
            <span className="text-[10px] font-mono uppercase font-bold tracking-widest">CHAIN OF CUSTODY</span>
          </div>
          <span className="text-[10px] font-mono text-slate-500">DPDP Act 2023 Compliant</span>
        </div>
        <h4 className="text-sm font-bold text-white mb-2">SHA-256 Tamper-Evident Forensic Hashing</h4>
        <p className="text-xs text-slate-400 mb-3">
          Every evidence clip, bounding box coordinate, and operator acknowledgment is cryptographically sealed with the prior log hash to establish court-admissible legal chain of custody.
        </p>
        <div className="p-2 rounded-lg bg-black/40 border border-slate-800 text-[10px] font-mono text-emerald-400 truncate">
          SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
        </div>
      </div>
    </div>
  );
};
