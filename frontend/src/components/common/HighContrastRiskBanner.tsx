import React from 'react';
import { AlertOctagon, ShieldAlert, X } from 'lucide-react';
import { useTacticalStore } from '../../store/useTacticalStore';

interface HighContrastRiskBannerProps {
  currentScore?: number;
  criticalMessage?: string;
  onAcknowledge?: () => void;
}

export const HighContrastRiskBanner: React.FC<HighContrastRiskBannerProps> = ({
  currentScore,
  criticalMessage = 'CRITICAL PERIMETER BREACH & MULTI-OBJECT INTRUSION SPIKE',
  onAcknowledge
}) => {
  const { threatLevel, setThreatLevel } = useTacticalStore();
  const effectiveScore = currentScore ?? (threatLevel === 'CRITICAL' ? 115 : 65);
  const isCritical = threatLevel === 'CRITICAL' || (currentScore !== undefined && currentScore >= 90);
  const [dismissed, setDismissed] = React.useState(false);

  // Reset dismissal if threat changes back to CRITICAL
  React.useEffect(() => {
    if (isCritical) {
      setDismissed(false);
    }
  }, [isCritical]);

  if (!isCritical || dismissed) {
    return null;
  }

  const handleAck = () => {
    setDismissed(true);
    if (onAcknowledge) onAcknowledge();
  };

  return (
    <>
      {/* Viewport High-Contrast Flashing Tactical Perimeter Border */}
      <div className="fixed inset-0 pointer-events-none border-4 border-rose-500/70 shadow-[inset_0_0_60px_rgba(244,63,94,0.35)] animate-pulse z-40" />

      {/* Top High-Contrast Anomaly Spike HUD Banner */}
      <div className="w-full bg-gradient-to-r from-rose-950 via-rose-900 to-rose-950 border-b-2 border-rose-500 text-rose-100 px-4 py-2.5 z-50 flex items-center justify-between shadow-2xl animate-fade-in">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-rose-600 border border-rose-400 flex items-center justify-center animate-ping">
            <AlertOctagon className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono text-xs font-black tracking-widest bg-rose-500 text-slate-950 px-2 py-0.5 rounded">
                ESCALATION PROTOCOL ACTIVE
              </span>
              <span className="font-mono text-xs font-black text-rose-300">
                RISK SCORE: {effectiveScore} / 120+ (CRITICAL)
              </span>
            </div>
            <p className="text-xs font-mono font-bold text-white mt-0.5">
              {criticalMessage}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleAck}
            className="px-3 py-1.5 rounded-lg bg-rose-500 hover:bg-rose-400 text-slate-950 font-mono font-black text-xs transition-all flex items-center space-x-1.5 shadow-lg cursor-pointer"
          >
            <ShieldAlert className="w-4 h-4" />
            <span>ACK ESCALATION</span>
          </button>
          <button
            onClick={() => setDismissed(true)}
            className="p-1 rounded text-rose-400 hover:text-white"
            title="Dismiss Banner"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </>
  );
};
