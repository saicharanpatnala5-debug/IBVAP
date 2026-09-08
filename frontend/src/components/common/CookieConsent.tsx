import React, { useState, useEffect } from 'react';
import { ShieldCheck, Check } from 'lucide-react';

export const CookieConsent: React.FC = () => {
  const [acknowledged, setAcknowledged] = useState<boolean>(true);

  useEffect(() => {
    const hasConsent = localStorage.getItem('ibvap_telemetry_acknowledged');
    if (!hasConsent) setAcknowledged(false);
  }, []);

  const handleAccept = () => {
    localStorage.setItem('ibvap_telemetry_acknowledged', 'true');
    setAcknowledged(true);
  };

  if (acknowledged) return null;

  return (
    <aside aria-label="Tactical telemetry notice" className="fixed bottom-4 right-4 z-50 max-w-md p-4 rounded-2xl liquid-glass border border-emerald-500/30 shadow-2xl animate-fade-in">
      <div className="flex items-start space-x-3">
        <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/40 text-emerald-400 mt-0.5">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <h4 className="text-xs font-bold text-slate-100 uppercase tracking-wider font-mono">
            DPDP Act 2023 & MoD Telemetry Policy
          </h4>
          <p className="text-xs text-slate-300 mt-1 leading-relaxed">
            This operational dashboard logs encrypted operator telemetry and forensic audit hashes to ensure tamper-evident zero-trust compliance.
          </p>
          <div className="mt-3 flex items-center space-x-2">
            <button
              onClick={handleAccept}
              className="px-3 py-1.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-obsidian font-bold text-xs font-mono flex items-center space-x-1.5 transition-all shadow-tactical-glow"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Acknowledge Protocol</span>
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
};
