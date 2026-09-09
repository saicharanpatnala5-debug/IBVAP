import React, { useState, useRef, useEffect } from 'react';
import { 
  Radio, UploadCloud, Video, Film, Wifi, ArrowUpRight, 
  Play, Pause, RotateCcw, ShieldAlert, Cpu, Sparkles, Plus, 
  CheckCircle2, ChevronRight, Repeat, Maximize, FileVideo, Check
} from 'lucide-react';
import { Camera, TacticalDetection } from '../../types';
import { TacticalDetectionOverlay } from './TacticalDetectionOverlay';
import { getDetectionsForTime, registerVideoBlob, computeTelemetry, captureAndInferFrame } from '../../utils/detectionEngine';
import { CurrentVideoContext } from '../../store/useVideoPlayerState';

interface TacticalIngestionHubProps {
  onOpenUploadModal: (videoUrl?: string, videoTitle?: string) => void;
  onOpenConnectModal: () => void;
  onSelectCamera?: (cameraId: string) => void;
}

interface ScenarioOption {
  id: string;
  name: string;
  url: string;
  duration: string;
}

const SAMPLE_SCENARIOS: ScenarioOption[] = [
  { id: 'scen-01', name: 'Perimeter Breach', url: '/videos/scenario_01_perimeter_breach.mp4', duration: '00:12' },
  { id: 'scen-02', name: 'Night Thermal Patrol', url: '/videos/scenario_02_night_thermal_patrol.mp4', duration: '00:24' },
  { id: 'scen-03', name: 'Checkpoint ANPR Scan', url: '/videos/scenario_03_checkpoint_anpr.mp4', duration: '00:15' },
  { id: 'scen-04', name: 'Multi-Camera Handoff', url: '/videos/scenario_04_multicam_handoff.mp4', duration: '00:30' },
  { id: 'scen-05', name: 'Dahua 4K Night Surveillance', url: '/videos/night-time---8mp-4k-dahua-cctv-system-sample-video.mp4', duration: '00:12' },
];

export const TacticalIngestionHub: React.FC<TacticalIngestionHubProps> = ({
  onOpenUploadModal,
  onOpenConnectModal,
  onSelectCamera,
}) => {
  const [activeTab, setActiveTab] = useState<'live' | 'upload'>('upload');

  // Inline Footage Player State
  const [activeFootageUrl, setActiveFootageUrl] = useState<string>(SAMPLE_SCENARIOS[1].url);
  const [activeFootageTitle, setActiveFootageTitle] = useState<string>(SAMPLE_SCENARIOS[1].name);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [currentVideoContext, setCurrentVideoContext] = useState<CurrentVideoContext | null>(null);
  const [trackingArrays, setTrackingArrays] = useState<TacticalDetection[]>([]);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [isLooping, setIsLooping] = useState<boolean>(true);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.loop = isLooping;
      videoRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
    }
  }, [activeFootageUrl, isLooping]);

  /**
   * STRICT TEARDOWN & VIDEO MEMORY FLUSH
   * Before initializing any new video stream:
   * 1. Clears previous video's canvas context
   * 2. Resets all tracking arrays to []
   * 3. Flushes currentVideoContext to null
   * 4. Revokes previous blob URLs and unloads HTML5 video buffers
   */
  const strictTeardownVideoMemory = () => {
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath();
      }
    }
    setTrackingArrays([]);
    setCurrentVideoContext(null);

    if (activeFootageUrl && activeFootageUrl.startsWith('blob:')) {
      try {
        URL.revokeObjectURL(activeFootageUrl);
      } catch (e) {
        console.warn('Failed to revoke blob URL:', e);
      }
    }
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.removeAttribute('src');
      videoRef.current.load();
    }
    setIsPlaying(false);
    setCurrentTime(0);
  };

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

  const processFile = (file: File) => {
    // MUST explicitly call strict teardown function before initializing new video stream
    strictTeardownVideoMemory();

    setActiveFootageTitle(file.name);
    const url = URL.createObjectURL(file);
    registerVideoBlob(url, file.name);
    setActiveFootageUrl(url);

    const initialDetections = getDetectionsForTime(file.name, 0, 30, url);
    setTrackingArrays(initialDetections);

    setCurrentVideoContext({
      streamId: `stream-${Date.now()}`,
      fileName: file.name,
      videoUrl: url,
      fps: 30.0,
      resolution: '1920x1080',
      duration: 0,
      currentTime: 0,
      status: 'LOADING',
      activeModel: 'yolo26x',
      sourceType: 'LOCAL_UPLOAD',
      telemetry: computeTelemetry(initialDetections),
      createdAt: new Date().toISOString()
    });

    setTimeout(() => {
      if (videoRef.current) {
        videoRef.current.currentTime = 0;
        videoRef.current.loop = isLooping;
        videoRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
      }
    }, 100);

    setTimeout(() => {
      inferHubFrame();
    }, 400);
  };

  const inferHubFrame = async () => {
    if (!videoRef.current || videoRef.current.videoWidth === 0) return;
    try {
      const res = await captureAndInferFrame(
        videoRef.current,
        activeFootageTitle.replace(/[^a-zA-Z0-9]/g, '_'),
        activeFootageUrl.includes('thermal')
      );
      if (res?.detections && res.detections.length > 0) {
        setTrackingArrays(res.detections);
      }
    } catch {
      // silent
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('video/')) {
      processFile(file);
    }
  };

  const formatTime = (secs: number) => {
    if (isNaN(secs)) return '00:00';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="rounded-3xl liquid-glass border border-slate-800 p-6 space-y-5 shadow-2xl relative overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header with Title and Mode Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 relative z-10 border-b border-slate-800/80 pb-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
            <h3 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
              Tactical Video Ingestion & Live Streams Hub
            </h3>
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
              OPERATIONAL
            </span>
          </div>
          <p className="text-xs font-mono text-slate-400">
            Upload & view surveillance footage with seamless looping, or connect to live multi-spectral RTSP camera streams
          </p>
        </div>

        {/* Dual Tab Switcher */}
        <div className="flex items-center p-1 rounded-2xl bg-slate-900/90 border border-slate-800 self-start sm:self-auto">
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all ${
              activeTab === 'upload'
                ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-obsidian shadow-tactical-glow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <UploadCloud className="w-3.5 h-3.5" />
            <span>Upload CCTV Footage</span>
          </button>
          <button
            onClick={() => setActiveTab('live')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all ${
              activeTab === 'live'
                ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-obsidian shadow-tactical-glow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Radio className="w-3.5 h-3.5" />
            <span>Connect Live CCTV</span>
          </button>
        </div>
      </div>

      {/* Tab 1: Upload & Interactive Footage Viewer */}
      {activeTab === 'upload' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center relative z-10 animate-fade-in">
          
          {/* Left Column: Interactive Video Player Playing on Loop */}
          <div className="lg:col-span-7 space-y-3">
            <div className="relative aspect-video rounded-2xl bg-black border border-slate-800 overflow-hidden shadow-2xl group">
              <video
                ref={videoRef}
                src={activeFootageUrl}
                autoPlay
                loop={isLooping}
                muted
                playsInline
                className="w-full h-full object-contain"
                onTimeUpdate={() => {
                  if (videoRef.current) setCurrentTime(videoRef.current.currentTime);
                }}
                onLoadedMetadata={() => {
                  if (videoRef.current) {
                    setDuration(videoRef.current.duration);
                    videoRef.current.loop = isLooping;
                    videoRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
                    setTimeout(inferHubFrame, 300);
                  }
                }}
                onPlay={() => {
                  setIsPlaying(true);
                  inferHubFrame();
                }}
              />

              {/* Hardware-accelerated canvas for frame extraction and optical flow overlays */}
              <canvas
                ref={canvasRef}
                className="absolute inset-0 pointer-events-none w-full h-full z-10"
              />

              {/* Real-time Multi-Class Tactical Detection Overlay */}
              <TacticalDetectionOverlay
                detections={trackingArrays.length > 0 ? trackingArrays : getDetectionsForTime(activeFootageTitle, currentTime, duration, activeFootageUrl)}
                cameraName={activeFootageTitle}
                fps={25.0}
                coordinates={duration > 0 && activeFootageUrl ? "28.6139° N, 77.2090° E" : undefined}
              />
            </div>

            {/* In-Line Player Controls: Play, Scrub, Loop Toggle, Fullscreen */}
            <div className="rounded-xl p-3 bg-slate-900/90 border border-slate-800 flex items-center justify-between gap-3">
              <div className="flex items-center space-x-2">
                <button
                  onClick={togglePlay}
                  className="p-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-obsidian font-bold transition-all shadow-tactical-glow"
                  title={isPlaying ? 'Pause' : 'Play'}
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
                  className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white"
                  title="Rewind"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>

                {/* LOOP TOGGLE BUTTON */}
                <button
                  onClick={toggleLoop}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold flex items-center space-x-1.5 border transition-all ${
                    isLooping
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50 shadow-[0_0_10px_rgba(16,185,129,0.3)]'
                      : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
                  }`}
                  title="Toggle Video Loop"
                >
                  <Repeat className={`w-3.5 h-3.5 ${isLooping ? 'animate-spin-slow' : ''}`} />
                  <span>LOOP: {isLooping ? 'ON' : 'OFF'}</span>
                </button>
              </div>

              {/* Scrub Slider */}
              <div className="flex-1 flex items-center space-x-2 px-2">
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

              <button
                onClick={() => onOpenUploadModal(activeFootageUrl, activeFootageTitle)}
                className="px-3 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-mono font-bold flex items-center space-x-1"
                title="Expand to Full Forensic Workstation"
              >
                <Maximize className="w-3.5 h-3.5" />
                <span>Expand</span>
              </button>
            </div>
          </div>

          {/* Right Column: Upload Input & Quick Scenarios */}
          <div className="lg:col-span-5 space-y-4">
            <div className="space-y-1">
              <span className="px-2.5 py-0.5 rounded bg-purple-500/20 text-purple-300 text-[10px] font-mono font-bold border border-purple-500/40">
                FORENSIC AI SUITE: YOLO26-X / ANPR OCR
              </span>
              <h4 className="text-base font-bold text-white font-mono mt-1">
                Select Surveillance Scenario or Upload File
              </h4>
              <p className="text-xs text-slate-400 font-mono">
                Footage plays continuously on loop for surveillance inspection and automated target recognition.
              </p>
            </div>

            {/* Quick Scenario Buttons */}
            <div className="space-y-1.5">
              <span className="text-[10px] font-mono text-slate-400 uppercase">Pre-Loaded Incident Scenarios:</span>
              <div className="grid grid-cols-2 gap-2">
                {SAMPLE_SCENARIOS.map((scen) => {
                  const isCurrent = activeFootageUrl === scen.url;
                  return (
                    <button
                      key={scen.id}
                      onClick={() => {
                        setActiveFootageUrl(scen.url);
                        setActiveFootageTitle(scen.name);
                      }}
                      className={`p-2 rounded-xl border text-left text-xs font-mono transition-all flex items-center justify-between ${
                        isCurrent
                          ? 'bg-emerald-500/20 border-emerald-500 text-white font-bold shadow-tactical-glow'
                          : 'bg-slate-900/70 border-slate-800 text-slate-300 hover:bg-slate-800'
                      }`}
                    >
                      <span className="truncate pr-1">{scen.name}</span>
                      <span className="text-[9px] px-1 py-0.5 rounded bg-slate-800 text-slate-400 flex-shrink-0">
                        {scen.duration}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Upload File Input with Drag and Drop Support */}
            <div 
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`p-3.5 rounded-2xl border border-dashed transition-all flex items-center space-x-3 cursor-pointer group ${
                isDragging
                  ? 'border-cyan-400 bg-cyan-500/20 shadow-tactical-glow'
                  : 'border-cyan-500/40 hover:border-cyan-400 bg-slate-900/60 hover:bg-cyan-500/10'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*,.mp4,.avi,.mkv,.mov,.webm"
                onChange={handleFileUpload}
                className="hidden"
              />
              <div className="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition-transform flex-shrink-0">
                <FileVideo className="w-5 h-5" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-mono font-bold text-white group-hover:text-cyan-300">
                  Upload Custom Surveillance Video
                </p>
                <p className="text-[10px] font-mono text-slate-400 truncate">
                  MP4, AVI, MKV, MOV (Drag & drop or click • Auto-plays on loop)
                </p>
              </div>
            </div>

            {/* Actions: Run Analysis in Workstation */}
            <div className="flex items-center space-x-2 pt-1">
              <button
                onClick={() => onOpenUploadModal(activeFootageUrl, activeFootageTitle)}
                className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-obsidian font-mono font-bold text-xs flex items-center justify-center space-x-2 transition-all shadow-tactical-glow"
              >
                <Cpu className="w-4 h-4" />
                <span>Run AI Detection Pipeline</span>
              </button>
            </div>
          </div>

        </div>
      )}

      {/* Tab 2: Connect Live CCTV Stream */}
      {activeTab === 'live' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center relative z-10 animate-fade-in">
          
          {/* Quick Connect Overview */}
          <div className="lg:col-span-7 space-y-4">
            <div className="flex items-center space-x-2">
              <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 text-[10px] font-mono font-bold border border-cyan-500/40">
                DIRECT PROTOCOLS: RTSP / ONVIF / HLS / WEBRTC
              </span>
              <span className="text-xs text-slate-400 font-mono">14.8 ms Edge Relay</span>
            </div>

            <h4 className="text-lg font-bold text-white font-mono leading-snug">
              Establish Immediate Low-Latency Connection to High-Mast & Perimeter Cameras
            </h4>

            <p className="text-xs text-slate-300 font-mono leading-relaxed">
              Connect directly to forward sensor nodes, PTZ towers, and mobile surveillance units across Sector A through D. Features automated telemetry health checks, packet loss monitoring, and motorized PTZ steering.
            </p>

            {/* Feature Badges */}
            <div className="grid grid-cols-3 gap-3 pt-1">
              <div className="bg-slate-900/70 p-3 rounded-xl border border-slate-800/80">
                <span className="text-[10px] text-slate-400 font-mono block">HW ACCELERATION</span>
                <span className="text-xs font-mono font-bold text-emerald-400">Jetson NVDEC 4K</span>
              </div>
              <div className="bg-slate-900/70 p-3 rounded-xl border border-slate-800/80">
                <span className="text-[10px] text-slate-400 font-mono block">FPS STABILITY</span>
                <span className="text-xs font-mono font-bold text-cyan-400">25–30 FPS Locked</span>
              </div>
              <div className="bg-slate-900/70 p-3 rounded-xl border border-slate-800/80">
                <span className="text-[10px] text-slate-400 font-mono block">TRANSPORT MODE</span>
                <span className="text-xs font-mono font-bold text-white">TCP Interleaved</span>
              </div>
            </div>

            <div className="pt-2 flex items-center space-x-3">
              <button
                onClick={onOpenConnectModal}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-obsidian font-mono font-bold text-xs flex items-center space-x-2 transition-all shadow-tactical-glow"
              >
                <Plus className="w-4 h-4" />
                <span>Connect New Live CCTV Stream</span>
              </button>
              <button
                onClick={() => onSelectCamera && onSelectCamera('CAM-03')}
                className="px-4 py-2.5 rounded-xl bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700 font-mono text-xs flex items-center space-x-1.5 transition-colors"
              >
                <span>Preview Thermal Feed (CAM-03)</span>
                <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
              </button>
            </div>
          </div>

          {/* Live Preview Card */}
          <div className="lg:col-span-5">
            <div 
              onClick={onOpenConnectModal}
              className="group cursor-pointer rounded-2xl bg-black border border-slate-800 overflow-hidden relative aspect-video shadow-2xl transition-all hover:border-emerald-500/60"
            >
              <video
                src="/videos/scenario_02_night_thermal_patrol.mp4"
                className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
                autoPlay
                loop
                muted
                playsInline
              />

              {/* HUD Badge Overlay */}
              <div className="absolute inset-0 p-3 flex flex-col justify-between pointer-events-none font-mono text-[10px]">
                <div className="flex items-center justify-between">
                  <span className="px-2 py-0.5 rounded bg-black/80 text-emerald-400 border border-emerald-500/40 font-bold flex items-center space-x-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping" />
                    <span>LIVE RTSP RELAY</span>
                  </span>
                  <span className="px-2 py-0.5 rounded bg-black/80 text-white border border-slate-700">
                    25.0 FPS | 1080p
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-slate-300 bg-black/70 px-2 py-0.5 rounded">
                    CAM-03 (Sector A Zero-Line)
                  </span>
                  <span className="text-cyan-400 group-hover:translate-x-0.5 transition-transform flex items-center space-x-1 bg-black/70 px-2 py-0.5 rounded">
                    <span>Configure Feed</span>
                    <ArrowUpRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            </div>
          </div>

        </div>
      )}

    </div>
  );
};
