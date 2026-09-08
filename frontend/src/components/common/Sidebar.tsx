import React from 'react';
import { LayoutDashboard, Video, Bell, ChevronLeft, ChevronRight } from 'lucide-react';
import { useTacticalStore } from '../../store/useTacticalStore';
import { useAlerts } from '../../hooks/useAlerts';

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onNavigate }) => {
  const { sidebarCollapsed, toggleSidebar } = useTacticalStore();
  const { alerts } = useAlerts();

  const activeAlertsCount = alerts.filter((a) => a.status === 'ACTIVE' || !a.is_acknowledged).length;

  // Streamlined MVP tactical navigation rail: Only core functioning operational routes
  const navItems = [
    { id: 'dashboard', label: 'Command Post', icon: LayoutDashboard },
    { id: 'live', label: 'Live Monitoring', icon: Video },
    { 
      id: 'alerts', 
      label: 'Tactical Alerts', 
      icon: Bell, 
      badge: activeAlertsCount > 0 ? String(activeAlertsCount) : undefined 
    },
  ];

  return (
    <aside 
      className={`relative z-30 flex flex-col border-r border-slate-800/80 bg-obsidian/95 backdrop-blur-xl transition-all duration-300 ${
        sidebarCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      <button 
        onClick={toggleSidebar}
        className="absolute -right-3 top-6 z-40 w-6 h-6 rounded-full bg-slate-800 border border-slate-700 text-slate-400 hover:text-white flex items-center justify-center shadow-lg transition-colors cursor-pointer"
        title={sidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        aria-label={sidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
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
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all group cursor-pointer ${
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
      </div>

      {!sidebarCollapsed && (
        <div className="p-3 m-2 rounded-xl bg-slate-900/60 border border-slate-800 text-[11px] font-mono">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span>Edge Latency</span>
            <span className="text-emerald-400 font-bold">14.2 ms</span>
          </div>
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400 w-3/4"></div>
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
