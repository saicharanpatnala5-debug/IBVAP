import React, { useRef, useState, useEffect } from 'react';
import { HUDOverlay } from './HUDOverlay';
import { TacticalDetectionOverlay } from './TacticalDetectionOverlay';
import { Camera, DetectionClass, TacticalDetection } from '../../types';
import { getCameraVideoUrl } from '../../utils/videoFeeds';
import { captureAndInferFrame, computeTelemetry } from '../../utils/detectionEngine';
import { pushLiveAlert } from '../../hooks/useAlerts';
import { Alert } from '../../types';
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
  const [useDirectStream, setUseDirectStream] = useState<boolean>(false);

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

  // Real-time detections state strictly bound to backend FastAPI response (starts empty: [])
  const [detections, setDetections] = useState<TacticalDetection[]>([]);
  const isInferringRef = useRef<boolean>(false);
  const alertedTracksRef = useRef<Set<string>>(new Set());
  const telemetry = computeTelemetry(detections);

  // Clear detections & cache on stream or video reset
  useEffect(() => {
    alertedTracksRef.current.clear();
    setDetections([]);
  }, [camera.camera_id, customVideoUrl]);

  // Real-time backend inference loop: queries FastAPI endpoint with live video frames
  useEffect(() => {
    let active = true;
    let timerId: any = null;

    const runInference = async () => {
      if (!active || !videoRef.current || videoRef.current.paused || videoRef.current.ended) {
        return;
      }
      if (isInferringRef.current) return;

      try {
        isInferringRef.current = true;
        const result = await captureAndInferFrame(
          videoRef.current,
          camera.camera_id,
          camera.sensor_type === 'THERMAL_LWIR'
        );

        if (active) {
          // Strictly bind detections state to backend response. If backend returns [], screen draws nothing.
          const freshDetections = Array.isArray(result) ? result : (Array.isArray(result?.detections) ? result.detections : []);
          setDetections(freshDetections);

          // Evaluate live detections for critical/high threats
          freshDetections.forEach((d: TacticalDetection) => {
            if (d.threat_level === 'CRITICAL' || d.threat_level === 'HIGH') {
              const dedupeKey = `${camera.camera_id}-${d.track_id}`;
              if (!alertedTracksRef.current.has(dedupeKey)) {
                alertedTracksRef.current.add(dedupeKey);

                const isCritical = d.threat_level === 'CRITICAL';
                const liveAlert: Alert = {
                  alert_id: `ALT-${Date.now().toString(36).toUpperCase()}-${d.track_id.replace(/[^a-zA-Z0-9]/g, '')}`,
                  camera_id: camera.camera_id,
                  severity: isCritical ? 'CRITICAL' : 'HIGH',
                  rule_triggered: isCritical ? 'ZONE_INTRUSION' : 'PERIMETER_BREACH',
                  message: `${d.label} [${d.track_id}] - Threat detected at ${camera.name || camera.camera_id}`,
                  risk_score: isCritical ? 95 : 75,
                  status: 'ACTIVE',
                  created_at: new Date().toISOString(),
                  confidence: d.confidence,
                };

                pushLiveAlert(liveAlert);
              }
            }
          });
        }
      } catch {
        if (active) setDetections([]);
      } finally {
        isInferringRef.current = false;
      }
    };

    // Continuous real-time inference loop while playing
    timerId = setInterval(runInference, 320);

    return () => {
      active = false;
      clearInterval(timerId);
    };
  }, [camera.camera_id, camera.name, camera.sensor_type, customVideoUrl]);

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
        {useDirectStream && !videoSource.startsWith('blob:') ? (
          <div className="relative w-full h-full flex items-center justify-center bg-black overflow-hidden group">
            <img
              src={`http://localhost:8000/api/video_feed?video_path=${encodeURIComponent(videoSource)}&camera_id=${encodeURIComponent(camera.camera_id)}&is_thermal=${camera.sensor_type === 'THERMAL_LWIR'}`}
              alt={`AI Stream ${camera.name}`}
              className={`w-full h-full ${fitMode === 'contain' ? 'object-contain' : 'object-cover'}`}
              onError={(err) => {
                console.warn('Direct stream connection failed', err);
                setUseDirectStream(false);
              }}
            />
            {/* Top Tactical Status Badges */}
            <div className="absolute top-3 left-3 z-30 flex items-center space-x-2 bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-emerald-500/50 shadow-tactical-glow">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
              <span className="text-[11px] font-mono font-bold text-emerald-400">
                FASTAPI OPENCV AI STREAM
              </span>
            </div>
            <div className="absolute top-3 right-3 z-30 flex items-center space-x-2 bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-cyan-500/40">
              <span className="text-[10px] font-mono text-cyan-300 font-bold">
                ENGINE: YOLO26s-PERCEPTION | 30 FPS
              </span>
            </div>
          </div>
        ) : (
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
              } else {
                setIsPlaying(false);
              }
            }}
          />
        )}

        {/* Tactical Detection & Telemetry Overlay */}
        {(!useDirectStream || videoSource.startsWith('blob:')) && showHUD && (
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

          {/* Direct OpenCV Backend Stream Toggle */}
          <button
            onClick={() => setUseDirectStream(!useDirectStream)}
            className={`px-2.5 py-1.5 rounded-xl text-xs font-mono font-bold border transition-all flex items-center space-x-1.5 ${
              useDirectStream
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/60 shadow-[0_0_10px_rgba(16,185,129,0.3)]'
                : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
            }`}
            title="Toggle Direct OpenCV Backend Stream"
          >
            <Radio className="w-3.5 h-3.5" />
            <span>AI STREAM: {useDirectStream ? 'ON' : 'OFF'}</span>
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
