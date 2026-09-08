import React, { useRef, useState, useEffect } from 'react';
import { HUDOverlay } from './HUDOverlay';
import { TacticalDetectionOverlay } from './TacticalDetectionOverlay';
import { Camera, DetectionClass } from '../../types';
import { getCameraVideoUrl } from '../../utils/videoFeeds';
import { getDetectionsForTime, computeTelemetry } from '../../utils/detectionEngine';
import { 
  Play, Pause, RotateCcw, Repeat, Maximize, Volume2, VolumeX, 
  Radio, Scan, Crosshair, Camera as CameraIcon, User, Car, Sparkles
} from 'lucide-react';

interface LiveStreamPlayerProps {
  camera: Camera;
  customVideoUrl?: string;
  customVideoTitle?: string;
  onSnapshot?: () => void;
  onSelectTarget?: (targetId: string | null) => void;
}

export const LiveStreamPlayer: React.FC<LiveStreamPlayerProps> = ({ 
  camera, 
  customVideoUrl,
  customVideoTitle,
  onSnapshot,
  onSelectTarget 
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [isLooping, setIsLooping] = useState<boolean>(true);
  const [isMuted, setIsMuted] = useState<boolean>(true);
  const [showHUD, setShowHUD] = useState<boolean>(true);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [fitMode, setFitMode] = useState<'contain' | 'cover'>('cover');

  // Dynamic 4-class detection filter states
  const [activeClasses, setActiveClasses] = useState<Record<DetectionClass, boolean>>({
    person: true,
    vehicle: true,
    object: true,
    animal: true,
  });
  const [selectedTargetId, setSelectedTargetId] = useState<string | null>(null);

  const toggleClass = (cls: DetectionClass) => {
    setActiveClasses((prev) => ({ ...prev, [cls]: !prev[cls] }));
  };

  const videoSource = customVideoUrl || getCameraVideoUrl(camera.camera_id, camera.stream_url);

  // Compute synchronized detections for current playback timestamp with title hint
  const detections = getDetectionsForTime(
    customVideoTitle || customVideoUrl || camera.camera_id,
    currentTime,
    duration,
    customVideoTitle || customVideoUrl || camera.name
  );
  const telemetry = computeTelemetry(detections);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
      videoRef.current.loop = isLooping;
      videoRef.current.muted = isMuted;
      videoRef.current.play().then(() => setIsPlaying(true)).catch(() => {
        if (videoRef.current) {
          videoRef.current.muted = true;
          setIsMuted(true);
          videoRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
        }
      });
    }
  }, [camera.camera_id, customVideoUrl]);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.loop = isLooping;
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

  const toggleLoop = () => {
    const next = !isLooping;
    setIsLooping(next);
    if (videoRef.current) {
      videoRef.current.loop = next;
      if (videoRef.current.ended) {
        videoRef.current.currentTime = 0;
        videoRef.current.play().catch(() => {});
      }
    }
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    const next = !isMuted;
    videoRef.current.muted = next;
    setIsMuted(next);
  };

  const handleFullscreen = () => {
    if (!containerRef.current) return;
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(() => {});
    } else {
      containerRef.current.requestFullscreen().catch(() => {});
    }
  };

  const formatTime = (secs: number) => {
    if (isNaN(secs)) return '00:00';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-2">
      {/* Real-time Video Viewport */}
      <div 
        ref={containerRef}
        className="relative aspect-video rounded-3xl overflow-hidden bg-black border border-slate-800 shadow-2xl group flex items-center justify-center"
      >
        <video
          ref={videoRef}
          src={videoSource}
          autoPlay
          loop={isLooping}
          muted={isMuted}
          playsInline
          className={`w-full h-full ${fitMode === 'contain' ? 'object-contain' : 'object-cover'}`}
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
          onEnded={() => {
            if (isLooping && videoRef.current) {
              videoRef.current.currentTime = 0;
              videoRef.current.play().catch(() => {});
            }
          }}
        />

        {/* Tactical Detection & Telemetry Overlay */}
        {showHUD && (
          <TacticalDetectionOverlay 
            detections={detections}
            cameraName={camera.name} 
            fps={camera.fps} 
            coordinates={`${camera.latitude.toFixed(4)}° N, ${camera.longitude.toFixed(4)}° E`}
            activeClasses={activeClasses}
            onToggleClass={toggleClass}
            selectedTargetId={selectedTargetId}
            onSelectTarget={(id) => {
              setSelectedTargetId(id);
              if (onSelectTarget) onSelectTarget(id);
            }}
          />
        )}
      </div>

      {/* Professional CCTV VMS Control Ribbon */}
      <div className="rounded-2xl p-3 liquid-glass border border-slate-800 flex flex-wrap items-center justify-between gap-3 font-mono text-xs">
        
        {/* Playback Controls & Loop Status */}
        <div className="flex items-center space-x-2">
          <button
            onClick={togglePlay}
            className="p-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-obsidian font-bold transition-all shadow-tactical-glow"
            title={isPlaying ? 'Pause Feed' : 'Resume Live Feed'}
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
          </button>

          <button
            onClick={() => {
              if (videoRef.current) {
                videoRef.current.currentTime = 0;
                videoRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
              }
            }}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
            title="Rewind to Start"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          {/* Loop Mode Indicator Button */}
          <button
            onClick={toggleLoop}
            className={`px-3 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5 transition-all border ${
              isLooping
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50 shadow-[0_0_10px_rgba(16,185,129,0.3)]'
                : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
            }`}
            title="Continuous CCTV Loop Playback"
          >
            <Repeat className={`w-3.5 h-3.5 ${isLooping ? 'animate-spin-slow' : ''}`} />
            <span>LOOP: {isLooping ? 'ON' : 'OFF'}</span>
          </button>

          {/* Mute Button */}
          <button
            onClick={toggleMute}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
            title={isMuted ? 'Unmute Audio' : 'Mute Audio'}
          >
            {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4 text-cyan-400" />}
          </button>

          <span className="text-slate-400 text-[11px] hidden sm:inline ml-2">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>
        </div>

        {/* Scrubber Timeline */}
        <div className="flex-1 min-w-[140px] max-w-xs sm:max-w-md flex items-center px-2">
          <input
            type="range"
            min={0}
            max={duration || 100}
            step={0.1}
            value={currentTime}
            onChange={(e) => {
              const val = parseFloat(e.target.value);
              setCurrentTime(val);
              if (videoRef.current) videoRef.current.currentTime = val;
            }}
            className="w-full accent-emerald-500 h-1.5 bg-slate-800 rounded cursor-pointer"
          />
        </div>

        {/* View Options: Snapshot, Fit, HUD Toggle, Fullscreen */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => {
              if (onSnapshot) onSnapshot();
              else alert(`CCTV snapshot captured from ${camera.camera_id} at ${formatTime(currentTime)}.`);
            }}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 transition-colors border border-slate-700"
            title="Capture Instant Frame Snapshot"
          >
            <CameraIcon className="w-4 h-4" />
          </button>

          <button
            onClick={() => setFitMode(fitMode === 'cover' ? 'contain' : 'cover')}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono transition-colors border border-slate-700"
            title={`Toggle Aspect Fit: ${fitMode.toUpperCase()}`}
          >
            <Scan className="w-4 h-4" />
          </button>

          <button
            onClick={() => setShowHUD(!showHUD)}
            className={`px-3 py-1.5 rounded-xl border font-bold transition-colors ${
              showHUD
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-[0_0_10px_rgba(16,185,129,0.2)]'
                : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
            title="Toggle AI Detection HUD Overlay"
          >
            AI HUD {showHUD ? 'ON' : 'OFF'}
          </button>

          <button
            onClick={handleFullscreen}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors border border-slate-700"
            title="Fullscreen CCTV View"
          >
            <Maximize className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
};
