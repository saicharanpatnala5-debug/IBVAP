import React, { useState, useEffect, useRef } from 'react';
import { Shield, Bell, Clock, Radio, User, Volume2, VolumeX, Plus, WifiOff } from 'lucide-react';
import { useTacticalStore } from '../../store/useTacticalStore';
import { useAlerts } from '../../hooks/useAlerts';
import { getSeverityBadgeStyles } from '../../utils/formatters';
import { TacticalAuth } from '../../services/auth';
import { CCTVUploadModal } from '../video/CCTVUploadModal';
import { LiveCCTVConnectModal } from '../video/LiveCCTVConnectModal';
import { useOfflineSync } from '../../services/offlineSyncService';

interface NavbarProps {
  onNavigate?: (page: string) => void;
  activePage?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ onNavigate }) => {
  const { threatLevel, audioAlertsEnabled, toggleAudioAlerts } = useTacticalStore();
  const { alerts } = useAlerts();
  const { isOffline, bufferedCount } = useOfflineSync();
  const [currentTime, setCurrentTime] = useState<string>('');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false);
  const [isConnectModalOpen, setIsConnectModalOpen] = useState<boolean>(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const session = TacticalAuth.getSession() || TacticalAuth.getDefaultPreset('admin');
  const activeAlertsCount = alerts.filter((a) => a.status === 'ACTIVE' || !a.is_acknowledged).length;
  const threatStyles = getSeverityBadgeStyles(threatLevel);
  const formattedThreatLevel = threatLevel.charAt(0) + threatLevel.slice(1).toLowerCase();

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setCurrentTime(now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC');
    };
    update();
    const timer = setInterval(update, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleCCTVFileSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      setIsUploadModalOpen(true);
    }
  };

  const triggerUploadClick = () => {
    setIsUploadModalOpen(true);
  };

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-obsidian/95 backdrop-blur-xl px-4 py-2.5 flex items-center justify-between shadow-tactical">
        {/* Left: Station Identity */}
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => onNavigate && onNavigate('dashboard')}
            className="flex items-center space-x-2.5 group text-left focus:outline-none cursor-pointer"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 border border-emerald-500/40 flex items-center justify-center shadow-tactical-glow group-hover:border-emerald-400 transition-colors">
              <Shield className="w-5 h-5 text-emerald-400 animate-pulse-slow" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-mono text-sm font-black tracking-wider text-slate-100">IBVAP</span>
                <span className="text-[10px] font-bold tracking-wider px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  Tactical Command
                </span>
              </div>
              <p className="text-[11px] font-mono text-slate-400">BOP Alpha — Sector B Command</p>
            </div>
          </button>
        </div>

        {/* Center: Main Top Navigation Rail — High Prominence Ingestion Controls */}
        <div className="flex items-center space-x-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleCCTVFileSelected}
            accept="video/mp4,video/avi,video/mkv,video/webm,video/*"
            className="hidden"
          />

          {/* Button 1: [+ Upload CCTV File] */}
          <button
            onClick={triggerUploadClick}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-mono text-xs font-black transition-all shadow-md shadow-cyan-500/30 hover:scale-[1.03] active:scale-[0.98] cursor-pointer"
            title="Upload CCTV / Local Video Recording for Multi-Class AI Perception"
          >
            <Plus className="w-4 h-4 text-slate-950 stroke-[3]" />
            <span>[+ Upload CCTV File]</span>
          </button>

          {/* Button 2: [(•) Link Live RTSP Stream] */}
          <button
            onClick={() => setIsConnectModalOpen(true)}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-emerald-950/80 hover:bg-emerald-900/90 border-2 border-emerald-500/70 text-emerald-300 hover:text-white font-mono text-xs font-bold transition-all shadow-sm shadow-emerald-500/30 hover:scale-[1.03] active:scale-[0.98] cursor-pointer"
            title="Link Live IP / RTSP / ONVIF High-Throughput Video Stream"
          >
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span>[(•) Link Live RTSP Stream]</span>
          </button>
        </div>

        {/* Right: Telemetry & Controls */}
        <div className="flex items-center space-x-2.5">
          <div className="hidden xl:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs font-mono">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-300 font-semibold">{currentTime}</span>
          </div>

          <div className={`hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-lg border text-xs font-mono ${threatStyles.bg} ${threatStyles.border}`}>
            <Radio className={`w-3.5 h-3.5 ${threatStyles.text} animate-pulse`} />
            <span className={`${threatStyles.text} font-bold tracking-wider`}>
              Threat: {formattedThreatLevel}
            </span>
          </div>

          {isOffline && (
            <div className="flex items-center space-x-1 px-2 py-1 rounded bg-amber-500/20 border border-amber-500/40 text-amber-300 text-[10px] font-mono font-bold animate-pulse">
              <WifiOff className="w-3 h-3 text-amber-400" />
              <span>Offline ({bufferedCount})</span>
            </div>
          )}

          <button
            onClick={toggleAudioAlerts}
            title={audioAlertsEnabled ? 'Perimeter Audio Siren: ACTIVE' : 'Perimeter Audio Siren: MUTED'}
            className={`p-2 rounded-lg border transition-all cursor-pointer ${
              audioAlertsEnabled 
                ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/20' 
                : 'bg-slate-800/40 border-slate-700 text-slate-500 hover:text-slate-400'
            }`}
          >
            {audioAlertsEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
          </button>

          <button 
            onClick={() => onNavigate && onNavigate('alerts')}
            className="relative p-2 rounded-lg bg-slate-900/60 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 transition-colors cursor-pointer"
            title="View Active Alerts"
          >
            <Bell className="w-4 h-4 text-amber-400" />
            <span className="absolute -top-1 -right-1 min-w-4 h-4 px-1 rounded-full bg-rose-500 text-[9px] font-bold font-mono text-white flex items-center justify-center">
              {alerts.length}
            </span>
          </button>

          <div className="flex items-center space-x-2 pl-2 border-l border-slate-800">
            <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
              <User className="w-4 h-4" />
            </div>
            <div className="hidden lg:block text-left">
              <p className="text-xs font-medium text-slate-200">{session.full_name}</p>
              <p className="text-[10px] font-mono uppercase text-emerald-400">{session.role}</p>
            </div>
          </div>
        </div>

        <CCTVUploadModal
          isOpen={isUploadModalOpen}
          onClose={() => {
            setIsUploadModalOpen(false);
            setUploadedFile(null);
          }}
          onFuseToIncident={() => onNavigate && onNavigate('dashboard')}
        />

        <LiveCCTVConnectModal
          isOpen={isConnectModalOpen}
          onClose={() => setIsConnectModalOpen(false)}
          onConnectCamera={() => onNavigate && onNavigate('live')}
        />
      </header>
    </>
  );
};
