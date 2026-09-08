import React, { useState, useRef, useEffect } from 'react';
import { 
  Radio, Video, Wifi, CheckCircle2, AlertCircle, X, 
  RefreshCw, ArrowRight, Shield, Activity, Compass, 
  ChevronUp, ChevronDown, ChevronLeft, ChevronRight, Plus, Minus,
  Eye, Zap, Camera as CameraIcon
} from 'lucide-react';
import { Camera, SensorType } from '../../types';

interface LiveCCTVConnectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConnectCamera?: (camera: Camera) => void;
}

interface StreamPreset {
  id: string;
  name: string;
  sector: string;
  url: string;
  resolution: string;
  fps: number;
  sensorType: SensorType;
  sampleVideo: string;
  coordinates: string;
}

const STREAM_PRESETS: StreamPreset[] = [
  {
    id: 'CAM-01-PRESET',
    name: 'BOP Alpha - Main Approach Gate',
    sector: 'Sector-B',
    url: 'rtsp://192.168.1.101:554/live/ch0',
    resolution: '1920x1080',
    fps: 25.0,
    sensorType: 'OPTICAL_4K',
    sampleVideo: '/videos/scenario_01_perimeter_breach.mp4',
    coordinates: '28.6139° N, 77.2090° E'
  },
  {
    id: 'CAM-02-PRESET',
    name: 'BOP Alpha - Cargo Bay ANPR Checkpoint',
    sector: 'Sector-B',
    url: 'rtsp://192.168.1.102:554/live/anpr',
    resolution: '3840x2160',
    fps: 25.0,
    sensorType: 'ANPR_CAMERA',
    sampleVideo: '/videos/scenario_03_checkpoint_anpr.mp4',
    coordinates: '28.6145° N, 77.2095° E'
  },
  {
    id: 'CAM-03-PRESET',
    name: 'BOP Bravo - Thermal Zero-Line Physical Fence',
    sector: 'Sector-A',
    url: 'rtsp://192.168.1.103:554/live/thermal',
    resolution: '1920x1080',
    fps: 30.0,
    sensorType: 'THERMAL_LWIR',
    sampleVideo: '/videos/scenario_02_night_thermal_patrol.mp4',
    coordinates: '28.6152° N, 77.2081° E'
  },
  {
    id: 'CAM-04-PRESET',
    name: 'BOP Charlie - Riverine Flank Marsh Patrol',
    sector: 'Sector-C',
    url: 'rtsp://192.168.1.104:554/live/ch0',
    resolution: '1920x1080',
    fps: 25.0,
    sensorType: 'OPTICAL_4K',
    sampleVideo: '/videos/scenario_04_multicam_handoff.mp4',
    coordinates: '28.6128° N, 77.2110° E'
  }
];

export const LiveCCTVConnectModal: React.FC<LiveCCTVConnectModalProps> = ({ 
  isOpen, 
  onClose, 
  onConnectCamera 
}) => {
  const [protocol, setProtocol] = useState<'RTSP' | 'HLS' | 'WEBRTC'>('RTSP');
  const [streamUrl, setStreamUrl] = useState<string>('rtsp://192.168.1.101:554/live/ch0');
  const [cameraName, setCameraName] = useState<string>('BOP Alpha - Sector B Tactical Live');
  const [cameraId, setCameraId] = useState<string>('CAM-08');
  const [sector, setSector] = useState<string>('Sector-B');
  const [sensorType, setSensorType] = useState<SensorType>('OPTICAL_4K');
  const [resolution, setResolution] = useState<string>('1920x1080');
  const [targetFps, setTargetFps] = useState<number>(25.0);
  const [transportMode, setTransportMode] = useState<'TCP' | 'UDP'>('TCP');

  // Video feed simulation
  const [activeVideoSrc, setActiveVideoSrc] = useState<string>(STREAM_PRESETS[0].sampleVideo);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  // Diagnostics & Status
  const [isTestingPing, setIsTestingPing] = useState<boolean>(false);
  const [connectionStatus, setConnectionStatus] = useState<'IDLE' | 'TESTING' | 'CONNECTED' | 'ERROR'>('CONNECTED');
  const [diagnostics, setDiagnostics] = useState<{
    latency: number;
    jitter: number;
    bitrate: number;
    packetLoss: number;
  }>({
    latency: 12.4,
    jitter: 0.5,
    bitrate: 4096,
    packetLoss: 0.0
  });

  // PTZ State
  const [ptzState, setPtzState] = useState<{ pan: number; tilt: number; zoom: number }>({
    pan: 0,
    tilt: 0,
    zoom: 1
  });

  useEffect(() => {
    if (isOpen && videoRef.current) {
      videoRef.current.play().catch(() => {});
    }
  }, [isOpen, activeVideoSrc]);

  const handleSelectPreset = (preset: StreamPreset) => {
    setStreamUrl(preset.url);
    setCameraName(preset.name);
    setSector(preset.sector);
    setSensorType(preset.sensorType);
    setResolution(preset.resolution);
    setTargetFps(preset.fps);
    setActiveVideoSrc(preset.sampleVideo);
    setConnectionStatus('CONNECTED');
  };

  const handleTestConnection = () => {
    setIsTestingPing(true);
    setConnectionStatus('TESTING');

    setTimeout(() => {
      setIsTestingPing(false);
      if (streamUrl.trim()) {
        setConnectionStatus('CONNECTED');
        setDiagnostics({
          latency: Number((Math.random() * 8 + 10).toFixed(1)),
          jitter: Number((Math.random() * 0.4 + 0.2).toFixed(2)),
          bitrate: 4096,
          packetLoss: 0.0
        });
        if (videoRef.current) {
          videoRef.current.play().catch(() => {});
        }
      } else {
        setConnectionStatus('ERROR');
      }
    }, 800);
  };

  const handlePtzAction = (direction: string) => {
    setPtzState(prev => {
      switch (direction) {
        case 'UP': return { ...prev, tilt: Math.min(prev.tilt + 5, 45) };
        case 'DOWN': return { ...prev, tilt: Math.max(prev.tilt - 5, -45) };
        case 'LEFT': return { ...prev, pan: (prev.pan - 10 + 360) % 360 };
        case 'RIGHT': return { ...prev, pan: (prev.pan + 10) % 360 };
        case 'ZOOM_IN': return { ...prev, zoom: Math.min(prev.zoom + 0.2, 4) };
        case 'ZOOM_OUT': return { ...prev, zoom: Math.max(prev.zoom - 0.2, 1) };
        case 'RESET': return { pan: 0, tilt: 0, zoom: 1 };
        default: return prev;
      }
    });
  };

  const handleAddCameraToFleet = () => {
    const newCamera: Camera = {
      camera_id: cameraId || `CAM-${Math.floor(Math.random() * 900) + 100}`,
      name: cameraName,
      site: 'BOP-Alpha',
      sector: sector,
      latitude: 28.6139,
      longitude: 77.2090,
      stream_url: streamUrl,
      status: 'ONLINE',
      fps: targetFps,
      resolution: resolution,
      sensor_type: sensorType,
      is_active: true
    };

    if (onConnectCamera) {
      onConnectCamera(newCamera);
    }
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/85 backdrop-blur-md overflow-y-auto animate-fade-in">
      <div className="relative w-full max-w-6xl my-auto max-h-[94vh] bg-obsidian border border-slate-700/80 rounded-3xl shadow-2xl flex flex-col overflow-hidden">
        
        {/* Modal Header */}
        <div className="flex-shrink-0 flex items-center justify-between px-6 py-3.5 border-b border-slate-800 bg-slate-900/90 backdrop-blur-lg">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
              <Radio className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base font-bold text-white font-mono uppercase tracking-wide">
                  Connect Live CCTV Stream & IP Camera
                </h2>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  RTSP / ONVIF / HLS
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Establish direct low-latency RTSP/HLS connection to tactical border security cameras and PTZ towers
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Column: Live Stream Player & PTZ (7 Cols) */}
          <div className="lg:col-span-7 space-y-4">
            
            {/* Real-time Video Viewport */}
            <div className="relative aspect-video rounded-2xl bg-black border border-slate-800 overflow-hidden shadow-2xl group">
              <video
                ref={videoRef}
                src={activeVideoSrc}
                className="w-full h-full object-cover"
                autoPlay
                loop
                muted
                playsInline
              />

              {/* Tactical HUD Overlay */}
              <div className="absolute inset-0 pointer-events-none p-4 flex flex-col justify-between text-[11px] font-mono text-emerald-400">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 bg-black/70 px-2.5 py-1 rounded backdrop-blur-sm border border-emerald-500/30">
                    <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                    <span className="font-bold text-white">LIVE FEED</span>
                    <span>[{cameraId}]</span>
                  </div>
                  <div className="bg-black/70 px-2.5 py-1 rounded backdrop-blur-sm border border-emerald-500/30">
                    <span>{targetFps.toFixed(1)} FPS | {resolution}</span>
                  </div>
                </div>

                {/* Reticle with Pan/Tilt Coordinates */}
                <div className="self-center my-auto relative w-24 h-24 flex items-center justify-center opacity-60">
                  <div className="w-16 h-16 rounded-full border border-emerald-400/50 border-dashed" />
                  <div className="absolute w-2 h-2 bg-emerald-400 rounded-full" />
                  <div className="absolute top-0 w-0.5 h-3 bg-emerald-400" />
                  <div className="absolute bottom-0 w-0.5 h-3 bg-emerald-400" />
                  <div className="absolute left-0 h-0.5 w-3 bg-emerald-400" />
                  <div className="absolute right-0 h-0.5 w-3 bg-emerald-400" />
                  <div className="absolute -bottom-5 text-[9px] font-mono text-emerald-300">
                    AZ: {ptzState.pan}° | EL: {ptzState.tilt}° | {ptzState.zoom.toFixed(1)}x
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="bg-black/70 px-2.5 py-1 rounded backdrop-blur-sm border border-emerald-500/30">
                    <span>SENSOR: {sensorType}</span>
                  </div>
                  <div className="bg-black/70 px-2.5 py-1 rounded backdrop-blur-sm border border-emerald-500/30 text-cyan-300">
                    LATENCY: {diagnostics.latency}ms
                  </div>
                </div>
              </div>
            </div>

            {/* Stream Telemetry Ribbon */}
            <div className="grid grid-cols-4 gap-2">
              <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800 text-center font-mono">
                <span className="text-[10px] text-slate-400 block uppercase">STREAM STATUS</span>
                <span className={`text-xs font-bold ${
                  connectionStatus === 'CONNECTED' ? 'text-emerald-400' : 'text-amber-400'
                }`}>
                  {connectionStatus === 'CONNECTED' ? 'ONLINE (100%)' : connectionStatus}
                </span>
              </div>
              <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800 text-center font-mono">
                <span className="text-[10px] text-slate-400 block uppercase">ROUNDTRIP</span>
                <span className="text-xs font-bold text-cyan-400">{diagnostics.latency} ms</span>
              </div>
              <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800 text-center font-mono">
                <span className="text-[10px] text-slate-400 block uppercase">BITRATE</span>
                <span className="text-xs font-bold text-white">{diagnostics.bitrate} kbps</span>
              </div>
              <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800 text-center font-mono">
                <span className="text-[10px] text-slate-400 block uppercase">PACKET LOSS</span>
                <span className="text-xs font-bold text-emerald-400">{diagnostics.packetLoss}%</span>
              </div>
            </div>

            {/* Integrated Tactical PTZ Directional Controls */}
            <div className="rounded-2xl p-4 liquid-glass border border-slate-800 flex items-center justify-between">
              <div className="space-y-1">
                <span className="text-xs font-mono font-bold text-white uppercase flex items-center space-x-1.5">
                  <Compass className="w-4 h-4 text-cyan-400" />
                  <span>PTZ Remote Actuator</span>
                </span>
                <p className="text-[10px] font-mono text-slate-400">
                  Control motorized pan, tilt, and optical zoom telemetry
                </p>
              </div>

              <div className="flex items-center space-x-4">
                {/* D-Pad */}
                <div className="grid grid-cols-3 gap-1 w-24">
                  <div />
                  <button 
                    onClick={() => handlePtzAction('UP')}
                    className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center"
                    title="Tilt Up"
                  >
                    <ChevronUp className="w-4 h-4" />
                  </button>
                  <div />
                  <button 
                    onClick={() => handlePtzAction('LEFT')}
                    className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center"
                    title="Pan Left"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => handlePtzAction('RESET')}
                    className="p-1.5 rounded bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 text-[9px] font-mono font-bold flex items-center justify-center"
                    title="Center"
                  >
                    CTR
                  </button>
                  <button 
                    onClick={() => handlePtzAction('RIGHT')}
                    className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center"
                    title="Pan Right"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                  <div />
                  <button 
                    onClick={() => handlePtzAction('DOWN')}
                    className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center"
                    title="Tilt Down"
                  >
                    <ChevronDown className="w-4 h-4" />
                  </button>
                  <div />
                </div>

                {/* Zoom */}
                <div className="flex flex-col space-y-1">
                  <button 
                    onClick={() => handlePtzAction('ZOOM_IN')}
                    className="p-2 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 flex items-center justify-center"
                    title="Zoom In"
                  >
                    <Plus className="w-3.5 h-3.5" />
                  </button>
                  <button 
                    onClick={() => handlePtzAction('ZOOM_OUT')}
                    className="p-2 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 flex items-center justify-center"
                    title="Zoom Out"
                  >
                    <Minus className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>

          </div>

          {/* Right Column: Connection Form & Presets (5 Cols) */}
          <div className="lg:col-span-5 space-y-4">
            
            {/* Quick Connect Presets */}
            <div className="rounded-2xl p-4 liquid-glass border border-slate-800 space-y-2.5">
              <span className="text-xs font-mono font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
                <Video className="w-4 h-4 text-emerald-400" />
                <span>Active Border Camera Presets</span>
              </span>

              <div className="grid grid-cols-1 gap-1.5 max-h-36 overflow-y-auto pr-1">
                {STREAM_PRESETS.map((preset) => (
                  <button
                    key={preset.id}
                    onClick={() => handleSelectPreset(preset)}
                    className={`w-full text-left p-2 rounded-xl border text-xs font-mono flex items-center justify-between transition-colors ${
                      streamUrl === preset.url
                        ? 'bg-emerald-500/20 border-emerald-500 text-white'
                        : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:bg-slate-800'
                    }`}
                  >
                    <div className="truncate pr-2">
                      <span className="font-bold">{preset.name}</span>
                      <span className="text-[10px] text-slate-400 block">{preset.url}</span>
                    </div>
                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-cyan-400 whitespace-nowrap">
                      {preset.sensorType.split('_')[0]}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Custom RTSP Stream Form */}
            <div className="rounded-2xl p-4 liquid-glass border border-slate-800 space-y-3 font-mono">
              <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
                <Wifi className="w-4 h-4 text-cyan-400" />
                <span>Stream Configuration</span>
              </span>

              {/* Protocol Selector */}
              <div className="grid grid-cols-3 gap-1.5 text-xs">
                {(['RTSP', 'HLS', 'WEBRTC'] as const).map((proto) => (
                  <button
                    key={proto}
                    onClick={() => setProtocol(proto)}
                    className={`py-1.5 rounded-lg border text-center font-bold transition-all ${
                      protocol === proto
                        ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300'
                        : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {proto}
                  </button>
                ))}
              </div>

              {/* Stream URL */}
              <div className="space-y-1">
                <label className="text-[10px] text-slate-400 uppercase">Stream Ingestion URL</label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={streamUrl}
                    onChange={(e) => setStreamUrl(e.target.value)}
                    placeholder="rtsp://192.168.1.100:554/live/ch0"
                    className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-400"
                  />
                  <button
                    onClick={handleTestConnection}
                    disabled={isTestingPing}
                    className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-cyan-400 text-xs flex items-center space-x-1"
                    title="Test Ping"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${isTestingPing ? 'animate-spin' : ''}`} />
                    <span>Ping</span>
                  </button>
                </div>
              </div>

              {/* Camera Name & ID */}
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <label className="text-[10px] text-slate-400 uppercase">Camera ID</label>
                  <input
                    type="text"
                    value={cameraId}
                    onChange={(e) => setCameraId(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-slate-400 uppercase">Sector</label>
                  <select
                    value={sector}
                    onChange={(e) => setSector(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400"
                  >
                    <option value="Sector-A">Sector-A (Zero Line)</option>
                    <option value="Sector-B">Sector-B (Approach Gate)</option>
                    <option value="Sector-C">Sector-C (Riverine)</option>
                    <option value="Sector-D">Sector-D (Watchtower)</option>
                  </select>
                </div>
              </div>

              {/* Sensor Modality & Transport */}
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <label className="text-[10px] text-slate-400 uppercase">Sensor Modality</label>
                  <select
                    value={sensorType}
                    onChange={(e) => setSensorType(e.target.value as SensorType)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400"
                  >
                    <option value="OPTICAL_4K">Optical 4K Daylight</option>
                    <option value="THERMAL_LWIR">Thermal LWIR Night</option>
                    <option value="ANPR_CAMERA">ANPR High-Speed</option>
                    <option value="STARLIGHT_PTZ">Starlight PTZ</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-slate-400 uppercase">RTSP Transport</label>
                  <select
                    value={transportMode}
                    onChange={(e) => setTransportMode(e.target.value as 'TCP' | 'UDP')}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400"
                  >
                    <option value="TCP">TCP Interleaved (Reliable)</option>
                    <option value="UDP">UDP Direct (Low Latency)</option>
                  </select>
                </div>
              </div>

              {/* Submit / Add to Fleet */}
              <div className="pt-2">
                <button
                  onClick={handleAddCameraToFleet}
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-obsidian font-mono font-bold text-xs flex items-center justify-center space-x-2 transition-all shadow-tactical-glow"
                >
                  <CameraIcon className="w-4 h-4" />
                  <span>Establish Stream & Add to Active Fleet</span>
                </button>
              </div>

            </div>

          </div>

        </div>

      </div>
    </div>
  );
};
