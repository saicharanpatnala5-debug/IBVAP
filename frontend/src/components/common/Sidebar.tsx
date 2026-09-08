import React from 'react';
import { 
  LayoutDashboard, Video, Camera, Bell, ShieldAlert, 
  Search, BarChart3, Map, Settings, Info, Mail, Sparkles, Award, ChevronLeft, ChevronRight
} from 'lucide-react';
import { useTacticalStore } from '../../store/useTacticalStore';

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onNavigate }) => {
  const { sidebarCollapsed, toggleSidebar } = useTacticalStore();

  const navItems = [
    { id: 'dashboard', label: 'Command Post', icon: LayoutDashboard },
    { id: 'live', label: 'Live Monitoring', icon: Video },
    { id: 'cameras', label: 'Camera Fleet', icon: Camera },
    { id: 'alerts', label: 'Tactical Alerts', icon: Bell, badge: '3' },
    { id: 'incidents', label: 'Fused Incidents', icon: ShieldAlert, badge: '1' },
    { id: 'search', label: 'ANPR & Face Analytics', icon: Search },
    { id: 'analytics', label: 'Defense Analytics', icon: BarChart3 },
    { id: 'map', label: 'Tactical GIS Map', icon: Map },
    { id: 'settings', label: 'System Weights', icon: Settings },
  ];

  const secondaryItems = [
    { id: 'contact', label: 'Notifications', icon: Mail },
  ];

  return (
    <aside 
      className={`relative z-30 flex flex-col border-r border-slate-800/80 bg-obsidian/95 backdrop-blur-xl transition-all duration-300 ${
        sidebarCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      <button 
        onClick={toggleSidebar}
        className="absolute -right-3 top-6 z-40 w-6 h-6 rounded-full bg-slate-800 border border-slate-700 text-slate-400 hover:text-white flex items-center justify-center shadow-lg transition-colors"
      >
        {sidebarCollapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
      </button>

      <div className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {!sidebarCollapsed && (
          <p className="px-3 text-[10px] font-mono uppercase tracking-widest text-slate-500 font-semibold mb-2">
            Tactical Operations
          </p>
        )}
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all group ${
                isActive
                  ? 'bg-gradient-to-r from-emerald-500/20 to-cyan-500/10 text-emerald-300 border-l-4 border-emerald-500 font-semibold shadow-tactical-glow'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
              }`}
              title={sidebarCollapsed ? item.label : undefined}
            >
              <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-emerald-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
              {!sidebarCollapsed && (
                <div className="flex-1 flex items-center justify-between">
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="px-1.5 py-0.5 rounded-full text-[9px] font-mono font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40">
                      {item.badge}
                    </span>
                  )}
                </div>
              )}
            </button>
          );
        })}

        <div className="pt-4 mt-4 border-t border-slate-800/80">
          {!sidebarCollapsed && (
            <p className="px-3 text-[10px] font-mono uppercase tracking-widest text-slate-500 font-semibold mb-2">
              Platform Settings
            </p>
          )}
          {secondaryItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-xl text-xs font-medium transition-all group ${
                  isActive
                    ? 'bg-slate-800/60 text-emerald-400 border-l-4 border-cyan-500'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
                }`}
                title={sidebarCollapsed ? item.label : undefined}
              >
                <Icon className="w-4 h-4 flex-shrink-0 text-slate-400 group-hover:text-slate-200" />
                {!sidebarCollapsed && <span>{item.label}</span>}
              </button>
            );
          })}
        </div>
      </div>

      {!sidebarCollapsed && (
        <div className="p-3 m-2 rounded-xl bg-slate-900/60 border border-slate-800 text-[11px] font-mono">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span>EDGE LATENCY</span>
            <span className="text-emerald-400 font-bold">14.2 ms</span>
          </div>
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400 w-3/4 animate-pulse"></div>
          </div>
          <p className="text-[10px] text-slate-500 mt-1.5 flex items-center space-x-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block"></span>
            <span>SIH26187 Edge Mesh Online</span>
          </p>
        </div>
      )}
    </aside>
  );
};
