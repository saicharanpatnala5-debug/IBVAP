import React, { useState, useEffect } from 'react';
import { Shield, Bell, Clock, Radio, User, Activity, Video, UploadCloud, Plus } from 'lucide-react';
import { useTacticalStore } from '../../store/useTacticalStore';
import { TacticalAuth } from '../../services/auth';
import { CCTVUploadModal } from '../video/CCTVUploadModal';
import { LiveCCTVConnectModal } from '../video/LiveCCTVConnectModal';

interface NavbarProps {
  onNavigate?: (page: string) => void;
  activePage?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ onNavigate }) => {
  const { threatLevel, audioAlertsEnabled, toggleAudioAlerts } = useTacticalStore();
  const [currentTime, setCurrentTime] = useState<string>('');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false);
  const [isConnectModalOpen, setIsConnectModalOpen] = useState<boolean>(false);
  const session = TacticalAuth.getSession() || TacticalAuth.getDefaultPreset('admin');

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setCurrentTime(now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC');
    };
    update();
    const timer = setInterval(update, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-obsidian/80 backdrop-blur-xl px-4 py-2.5 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <button 
          onClick={() => onNavigate && onNavigate('dashboard')}
          className="flex items-center space-x-2.5 group text-left focus:outline-none"
        >
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 border border-emerald-500/40 flex items-center justify-center shadow-tactical-glow group-hover:border-emerald-400 transition-colors">
            <Shield className="w-5 h-5 text-emerald-400 animate-pulse-slow" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="font-mono text-sm font-black tracking-wider text-slate-100">IBVAP</span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                TACTICAL POST
              </span>
            </div>
            <p className="text-[11px] font-mono text-slate-400">BOP Alpha — Sector B Command</p>
          </div>
        </button>
      </div>

      <div className="hidden md:flex items-center space-x-6 text-xs font-mono">
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900/60 border border-slate-800">
          <Clock className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-300 font-semibold">{currentTime}</span>
        </div>

        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-rose-500/10 border border-rose-500/40">
          <Radio className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
          <span className="text-rose-400 font-bold tracking-wider">SYSTEM STATUS: {threatLevel}</span>
        </div>
      </div>

      <div className="flex items-center space-x-2.5">
        {/* Quick Tactical Action Buttons */}
        <button
          onClick={() => setIsConnectModalOpen(true)}
          className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-mono text-xs font-semibold transition-all shadow-sm"
          title="Connect Live RTSP / IP Camera"
        >
          <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span>+ Connect Live</span>
        </button>

        <button
          onClick={() => setIsUploadModalOpen(true)}
          className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white font-mono text-xs transition-colors"
          title="Upload Surveillance Video for AI Detection"
        >
          <UploadCloud className="w-3.5 h-3.5 text-cyan-400" />
          <span>Upload CCTV</span>
        </button>

        <button
          onClick={toggleAudioAlerts}
          title={audioAlertsEnabled ? 'Audio Alarms Active' : 'Audio Alarms Muted'}
          className={`p-2 rounded-lg border transition-all ${
            audioAlertsEnabled 
              ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400' 
              : 'bg-slate-800/40 border-slate-700 text-slate-500'
          }`}
        >
          <Activity className="w-4 h-4" />
        </button>

        <button 
          onClick={() => onNavigate && onNavigate('alerts')}
          className="relative p-2 rounded-lg bg-slate-900/60 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 transition-colors"
        >
          <Bell className="w-4 h-4 text-amber-400" />
          <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-500 text-[9px] font-bold font-mono text-white flex items-center justify-center animate-bounce">
            3
          </span>
        </button>

        <div className="flex items-center space-x-2.5 pl-2 border-l border-slate-800">
          <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
            <User className="w-4 h-4" />
          </div>
          <div className="hidden lg:block text-left">
            <p className="text-xs font-medium text-slate-200">{session.full_name}</p>
            <p className="text-[10px] font-mono uppercase text-emerald-400">{session.role}</p>
          </div>
        </div>
      </div>

      {/* Global Ingestion Modals */}
      <CCTVUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onFuseToIncident={() => onNavigate && onNavigate('incidents')}
      />

      <LiveCCTVConnectModal
        isOpen={isConnectModalOpen}
        onClose={() => setIsConnectModalOpen(false)}
        onConnectCamera={() => onNavigate && onNavigate('live')}
      />
    </header>
  );
};
