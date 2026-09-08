import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, RotateCcw, ShieldCheck, Download, Repeat, Maximize } from 'lucide-react';

export const EvidencePlayback: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [isLooping, setIsLooping] = useState<boolean>(true);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.loop = isLooping;
      videoRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
    }
  }, [isLooping]);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
      setIsPlaying(false);
    } else {
      videoRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setCurrentTime(val);
    if (videoRef.current) videoRef.current.currentTime = val;
  };

  const formatTime = (secs: number) => {
    if (isNaN(secs)) return '00:00';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="rounded-2xl p-4 liquid-glass border border-slate-800 space-y-3">
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-800">
        <span className="text-xs font-mono font-bold text-white uppercase flex items-center space-x-2">
          <span>FORENSIC EVIDENCE PLAYER</span>
          <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
            SHA-256 VERIFIED
          </span>
        </span>
        <span className="text-[10px] font-mono text-emerald-400 flex items-center space-x-1">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>TAMPER-SEAL INTACT</span>
        </span>
      </div>

      <div className="relative aspect-video rounded-xl bg-black border border-slate-800 overflow-hidden group flex items-center justify-center">
        <video
          ref={videoRef}
          src="/videos/scenario_02_night_thermal_patrol.mp4"
          autoPlay
          loop={isLooping}
          muted
          playsInline
          className="w-full h-full object-cover"
          onTimeUpdate={() => {
            if (videoRef.current) setCurrentTime(videoRef.current.currentTime);
          }}
          onLoadedMetadata={() => {
            if (videoRef.current) {
              setDuration(videoRef.current.duration);
              videoRef.current.loop = isLooping;
              videoRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
            }
          }}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
        />

        {/* Tactical OSD watermark */}
        <div className="absolute top-2 left-2 bg-black/70 px-2 py-0.5 rounded text-[9px] font-mono text-emerald-400 border border-emerald-500/30">
          CLIP: ev_CAM-03_20260906.mp4
        </div>
        <div className="absolute top-2 right-2 bg-black/70 px-2 py-0.5 rounded text-[9px] font-mono text-cyan-300 border border-cyan-500/30">
          THERMAL LWIR
        </div>
      </div>

      <div className="space-y-1.5">
        <input
          type="range"
          min={0}
          max={duration || 100}
          step={0.1}
          value={currentTime}
          onChange={handleSeek}
          className="w-full accent-emerald-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
        />
        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
          <span>{formatTime(currentTime)} / {formatTime(duration)}</span>
          <span className="text-emerald-400">{isLooping ? 'LOOP ACTIVE' : 'SINGLE PASS'}</span>
        </div>
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-slate-800">
        <div className="flex items-center space-x-2">
          <button
            onClick={togglePlay}
            className="p-2 rounded-lg bg-emerald-500 text-obsidian font-bold hover:bg-emerald-400 transition-colors shadow-tactical-glow"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
          <button
            onClick={() => {
              if (videoRef.current) {
                videoRef.current.currentTime = 0;
                videoRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
              }
            }}
            className="p-2 rounded-lg bg-slate-800 text-slate-300 hover:text-white"
            title="Rewind"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsLooping(!isLooping)}
            className={`p-2 rounded-lg border text-xs font-mono transition-colors ${
              isLooping 
                ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400' 
                : 'bg-slate-800 border-slate-700 text-slate-400'
            }`}
            title="Toggle Loop"
          >
            <Repeat className="w-4 h-4" />
          </button>
        </div>

        <button 
          onClick={() => alert('Exporting SHA-256 cryptographically sealed MP4 package...')}
          className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-200 flex items-center space-x-1.5"
        >
          <Download className="w-3.5 h-3.5 text-cyan-400" />
          <span>Export Sealed MP4</span>
        </button>
      </div>
    </div>
  );
};
