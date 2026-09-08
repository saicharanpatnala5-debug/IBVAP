import React from 'react';
import { Check } from 'lucide-react';

interface TimelineStep {
  time: string;
  cameraId: string;
  action: string;
  status: 'COMPLETED' | 'ACTIVE';
}

export const IncidentTimeline: React.FC = () => {
  const steps: TimelineStep[] = [
    { time: '02:40:15 UTC', cameraId: 'CAM-01', action: 'Approach road loitering dwell limit exceeded (>45s)', status: 'COMPLETED' },
    { time: '02:40:48 UTC', cameraId: 'CAM-01', action: 'White recon vehicle sighted; ANPR match DL01AB1234', status: 'COMPLETED' },
    { time: '02:41:19 UTC', cameraId: 'CAM-03', action: 'Physical fence traversal on Restricted Zone Sector Line', status: 'ACTIVE' },
    { time: '02:41:35 UTC', cameraId: 'CAM-07', action: 'Predicted inward transit toward Strategic Communications Depot', status: 'ACTIVE' },
  ];

  return (
    <div className="rounded-2xl p-6 liquid-glass border border-slate-800">
      <h4 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider mb-4">
        MULTI-CAMERA CORRELATED TRAJECTORY TIMELINE
      </h4>

      <div className="relative pl-6 space-y-6 border-l-2 border-slate-800">
        {steps.map((step, idx) => (
          <div key={idx} className="relative group">
            <div className={`absolute -left-[31px] top-0.5 w-4 h-4 rounded-full border-2 flex items-center justify-center ${
              step.status === 'ACTIVE'
                ? 'bg-rose-500 border-rose-400 shadow-[0_0_10px_rgba(244,63,94,0.6)] animate-pulse'
                : 'bg-slate-800 border-emerald-500 text-emerald-400'
            }`}>
              {step.status === 'COMPLETED' && <Check className="w-2.5 h-2.5" />}
            </div>

            <div className="flex items-baseline space-x-2">
              <span className="text-[11px] font-mono font-bold text-cyan-400">{step.time}</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                {step.cameraId}
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">{step.action}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
