import React from 'react';

export const TacticalMap: React.FC = () => {
  return (
    <div className="relative w-full aspect-[16/9] md:aspect-[21/9] rounded-3xl bg-slate-950 border border-slate-800 overflow-hidden shadow-2xl p-4">
      <svg className="w-full h-full" viewBox="0 0 1000 500">
        <g stroke="rgba(255,255,255,0.05)" strokeWidth="1">
          {[...Array(20)].map((_, i) => (
            <line key={`x-${i}`} x1={i * 50} y1="0" x2={i * 50} y2="500" />
          ))}
          {[...Array(10)].map((_, i) => (
            <line key={`y-${i}`} x1="0" y1={i * 50} x2="1000" y2={i * 50} />
          ))}
        </g>

        <path
          d="M 50 120 L 300 140 L 600 130 L 950 150"
          fill="none"
          stroke="#f43f5e"
          strokeWidth="3"
          strokeDasharray="8 4"
        />
        <text x="60" y="105" fill="#f43f5e" fontSize="11" fontFamily="monospace" fontWeight="bold">
          INTERNATIONAL Restricted Zone BORDER LINE
        </text>

        <polygon
          points="100,160 400,180 850,190 900,320 150,300"
          fill="rgba(245, 158, 11, 0.08)"
          stroke="#f59e0b"
          strokeWidth="1.5"
          strokeDasharray="4 4"
        />
        <text x="180" y="240" fill="#f59e0b" fontSize="10" fontFamily="monospace">
          YELLOW_MONITORING ZONE (BUFFER)
        </text>

        {/* CAM-01 */}
        <path d="M 200 350 L 150 200 L 280 210 Z" fill="rgba(16, 185, 129, 0.15)" stroke="#10b981" strokeWidth="1" />
        <circle cx="200" cy="350" r="6" fill="#10b981" />
        <text x="212" y="355" fill="#fff" fontSize="10" fontFamily="monospace">CAM-01 (Approach Gate)</text>

        {/* CAM-03 */}
        <path d="M 550 220 L 480 120 L 640 125 Z" fill="rgba(244, 63, 94, 0.2)" stroke="#f43f5e" strokeWidth="1" />
        <circle cx="550" cy="220" r="6" fill="#f43f5e" />
        <text x="562" y="225" fill="#f43f5e" fontSize="10" fontFamily="monospace">CAM-03 [BREACH DETECTED]</text>

        <circle cx="560" cy="140" r="8" fill="#f43f5e">
          <animate attributeName="r" values="6;16;6" dur="1.5s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="1;0.2;1" dur="1.5s" repeatCount="indefinite" />
        </circle>
      </svg>

      <div className="absolute bottom-4 left-4 bg-obsidian/80 backdrop-blur-md px-3 py-2 rounded-xl border border-slate-800 text-[10px] font-mono text-slate-300">
        <p className="text-emerald-400 font-bold">BOP ALPHA SECTOR B — GIS RADAR</p>
        <p>CENTER: 28.6139° N, 77.2090° E | ELEV: 240M</p>
      </div>
    </div>
  );
};
