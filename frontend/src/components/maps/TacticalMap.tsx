import React from 'react';
import { Alert } from '../../types';
import { useAlerts } from '../../hooks/useAlerts';
import { Eye, Compass } from 'lucide-react';

interface TacticalMapProps {
  alerts?: Alert[];
  onSelectCamera?: (cameraId: string) => void;
}

interface MapCameraDef {
  id: string;
  name: string;
  cx: number;
  cy: number;
  fovPath: string;
  alertCoords?: { x: number; y: number };
}

const MAP_CAMERAS: MapCameraDef[] = [
  {
    id: 'CAM-01',
    name: 'CAM-01 (Approach Gate)',
    cx: 200,
    cy: 350,
    fovPath: 'M 200 350 L 140 220 L 270 230 Z',
  },
  {
    id: 'CAM-02',
    name: 'CAM-02 (Checkpoint ANPR)',
    cx: 380,
    cy: 310,
    fovPath: 'M 380 310 L 320 190 L 450 195 Z',
  },
  {
    id: 'CAM-03',
    name: 'CAM-03 (Perimeter Fence)',
    cx: 560,
    cy: 250,
    fovPath: 'M 560 250 L 480 135 L 630 140 Z',
    alertCoords: { x: 550, y: 155 },
  },
  {
    id: 'CAM-04',
    name: 'CAM-04 (Cargo Handoff)',
    cx: 730,
    cy: 290,
    fovPath: 'M 730 290 L 670 180 L 800 185 Z',
  },
  {
    id: 'CAM-05',
    name: 'CAM-05 (Dahua 4K Night)',
    cx: 870,
    cy: 260,
    fovPath: 'M 870 260 L 800 150 L 940 155 Z',
  },
];

export const TacticalMap: React.FC<TacticalMapProps> = ({ alerts: propAlerts, onSelectCamera }) => {
  const { alerts: hookAlerts } = useAlerts();
  const alerts = propAlerts || hookAlerts;

  // Single source of truth: actively unacknowledged alerts
  const activeAlertCameras = new Set(
    alerts
      .filter((a) => a.status === 'ACTIVE' || (!a.status && !(a as any).is_acknowledged))
      .map((a) => a.camera_id)
  );

  return (
    <div className="relative w-full aspect-[16/9] md:aspect-[21/9] rounded-3xl bg-slate-950 border border-slate-800 overflow-hidden shadow-2xl p-4">
      <svg className="w-full h-full" viewBox="0 0 1000 500">
        {/* Subtle GIS coordinate grid */}
        <g stroke="rgba(255,255,255,0.04)" strokeWidth="1">
          {[...Array(20)].map((_, i) => (
            <line key={`x-${i}`} x1={i * 50} y1="0" x2={i * 50} y2="500" />
          ))}
          {[...Array(10)].map((_, i) => (
            <line key={`y-${i}`} x1="0" y1={i * 50} x2="1000" y2={i * 50} />
          ))}
        </g>

        {/* International Border Line (Restricted Zero Line) */}
        <path
          d="M 50 100 L 300 120 L 600 110 L 950 130"
          fill="none"
          stroke="#f43f5e"
          strokeWidth="3"
          strokeDasharray="8 4"
        />
        <text x="60" y="88" fill="#f43f5e" fontSize="11" fontFamily="monospace" fontWeight="bold">
          International Border Line (Restricted Zero Line)
        </text>

        {/* Physical Security Fence Line */}
        <path
          d="M 60 140 L 310 160 L 610 150 L 960 170"
          fill="none"
          stroke="#94a3b8"
          strokeWidth="1.5"
          strokeDasharray="5 3"
        />
        <text x="70" y="132" fill="#94a3b8" fontSize="9" fontFamily="monospace">
          Physical Perimeter Security Fence (Sensored)
        </text>

        {/* Monitoring Buffer Zone (150m Corridor) */}
        <polygon
          points="80,165 400,185 860,195 910,315 130,295"
          fill="rgba(245, 158, 11, 0.06)"
          stroke="#f59e0b"
          strokeWidth="1.5"
          strokeDasharray="4 4"
        />
        <text x="160" y="235" fill="#f59e0b" fontSize="10" fontFamily="monospace">
          Monitoring Buffer Zone (150m Security Corridor)
        </text>

        {/* Tactical Cameras with Vision Coverage Cones & Dynamic Alert State */}
        {MAP_CAMERAS.map((cam) => {
          const hasAlert = activeAlertCameras.has(cam.id);
          const coneColor = hasAlert ? '#f43f5e' : '#10b981';
          const coneFill = hasAlert ? 'rgba(244, 63, 94, 0.22)' : 'rgba(16, 185, 129, 0.12)';

          return (
            <g 
              key={cam.id} 
              className="cursor-pointer group"
              onClick={() => onSelectCamera && onSelectCamera(cam.id)}
            >
              {/* Field-of-View (FOV) Directional Vision Cone */}
              <path
                d={cam.fovPath}
                fill={coneFill}
                stroke={coneColor}
                strokeWidth="1"
                className="transition-all duration-300 group-hover:fill-opacity-40"
              />

              {/* Camera Base Pole Node */}
              <circle
                cx={cam.cx}
                cy={cam.cy}
                r="6"
                fill={coneColor}
                className="transition-transform group-hover:scale-125"
              />
              <circle
                cx={cam.cx}
                cy={cam.cy}
                r="10"
                fill="none"
                stroke={coneColor}
                strokeWidth="1"
                opacity="0.4"
              />

              {/* Camera Status Label */}
              <text
                x={cam.cx + 12}
                y={cam.cy + 4}
                fill={hasAlert ? '#f43f5e' : '#cbd5e1'}
                fontSize="10"
                fontFamily="monospace"
                fontWeight={hasAlert ? 'bold' : 'normal'}
              >
                {cam.name} {hasAlert ? '[Breach Sighted]' : ''}
              </text>

              {/* Pulsing Active Breach Beacon ONLY if Alert is Active */}
              {hasAlert && cam.alertCoords && (
                <g>
                  <circle cx={cam.alertCoords.x} cy={cam.alertCoords.y} r="8" fill="#f43f5e">
                    <animate attributeName="r" values="6;18;6" dur="1.4s" repeatCount="indefinite" />
                    <animate attributeName="opacity" values="1;0.15;1" dur="1.4s" repeatCount="indefinite" />
                  </circle>
                  <circle cx={cam.alertCoords.x} cy={cam.alertCoords.y} r="4" fill="#fff" />
                </g>
              )}
            </g>
          );
        })}
      </svg>

      {/* Map Header & Geographical Position (Bottom Left) */}
      <div className="absolute bottom-4 left-4 bg-obsidian/85 backdrop-blur-md px-3.5 py-2.5 rounded-2xl border border-slate-800 text-[10px] font-mono text-slate-300 shadow-lg">
        <div className="flex items-center space-x-2">
          <Compass className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-emerald-400 font-bold">BOP Alpha Sector B — Tactical Radar</span>
        </div>
        <p className="text-slate-400 mt-0.5">
          Grid: 28.6139° N, 77.2090° E | Elevation: 240m AMSL
        </p>
      </div>

      {/* Explicit Map Legend (Top Right) */}
      <div className="absolute top-4 right-4 bg-obsidian/90 backdrop-blur-md p-3 rounded-2xl border border-slate-800 text-[10px] font-mono shadow-xl space-y-1.5 hidden sm:block max-w-xs">
        <div className="text-white font-bold tracking-wider text-[11px] border-b border-slate-800 pb-1 flex items-center justify-between">
          <span>Map Legend & Status</span>
          <Eye className="w-3 h-3 text-cyan-400" />
        </div>

        <div className="grid grid-cols-1 gap-1 pt-0.5 text-slate-300">
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 rounded-full bg-emerald-500/20 border border-emerald-500 flex-shrink-0" />
            <span>Camera Vision Cone (Normal Coverage)</span>
          </div>

          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 rounded-full bg-rose-500/20 border border-rose-500 flex-shrink-0" />
            <span className="text-rose-400 font-semibold">Active Alert / Breach Sector</span>
          </div>

          <div className="flex items-center space-x-2">
            <span className="w-3.5 h-0.5 border-b-2 border-dashed border-rose-500 flex-shrink-0" />
            <span>International Border Line (Restricted)</span>
          </div>

          <div className="flex items-center space-x-2">
            <span className="w-3.5 h-0.5 border-b-2 border-dashed border-slate-400 flex-shrink-0" />
            <span>Perimeter Security Fence</span>
          </div>

          <div className="flex items-center space-x-2">
            <span className="w-3.5 h-2 bg-amber-500/20 border border-amber-500/50 rounded-sm flex-shrink-0" />
            <span>Monitoring Buffer Zone (150m)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
