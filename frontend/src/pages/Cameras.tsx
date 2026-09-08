import React from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { useCameras } from '../hooks/useCameras';
import { SEOHead } from '../components/common/SEOHead';
import { Camera, Radio, Plus, CheckCircle, AlertTriangle } from 'lucide-react';

export const Cameras: React.FC = () => {
  const { cameras } = useCameras();

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto animate-fade-in">
      <SEOHead title="Camera Fleet Management" description="Surveillance sensor fleet and network topology" />

      <div className="flex items-center justify-between">
        <Breadcrumbs items={[{ label: 'Camera Fleet Inventory', isCurrent: true }]} />
        <button className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-obsidian font-bold text-xs font-mono flex items-center space-x-1.5 shadow-tactical-glow">
          <Plus className="w-4 h-4" />
          <span>Register Edge Sensor</span>
        </button>
      </div>

      <div className="rounded-3xl liquid-glass border border-slate-800 overflow-hidden shadow-2xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider">
            BORDER SECTOR CAMERA INVENTORY ({cameras.length})
          </h3>
          <span className="text-[10px] font-mono text-emerald-400">All Edge Feeds Active</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 text-[10px] uppercase">
              <tr>
                <th className="p-4">Camera ID</th>
                <th className="p-4">Designation</th>
                <th className="p-4">Sensor Type</th>
                <th className="p-4">FPS / Latency</th>
                <th className="p-4">Status</th>
                <th className="p-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {cameras.map((c) => (
                <tr key={c.camera_id} className="hover:bg-slate-900/40 transition-colors">
                  <td className="p-4 font-bold text-white">{c.camera_id}</td>
                  <td className="p-4 text-slate-300">{c.name}</td>
                  <td className="p-4 text-cyan-400">{c.sensor_type || 'OPTICAL_4K'}</td>
                  <td className="p-4 text-slate-400">{c.fps.toFixed(1)} FPS / 14ms</td>
                  <td className="p-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                      c.status === 'ONLINE'
                        ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                        : 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                    }`}>
                      {c.status}
                    </span>
                  </td>
                  <td className="p-4">
                    <button className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300">
                      Configure
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
