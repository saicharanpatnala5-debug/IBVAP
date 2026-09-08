import React from 'react';
import { SEOHead } from '../components/common/SEOHead';
import { CheckCircle2, Shield, ArrowRight, Home } from 'lucide-react';

interface ThankYouProps {
  onReturnHome: () => void;
}

export const ThankYou: React.FC<ThankYouProps> = ({ onReturnHome }) => {
  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <SEOHead title="Transmission Received" description="Cryptographic transmission acknowledgment" />

      <div className="max-w-lg w-full rounded-3xl p-8 liquid-glass-glow border-2 border-emerald-500/60 text-center shadow-2xl animate-fade-in">
        <div className="w-16 h-16 rounded-3xl bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center mx-auto mb-4 shadow-tactical-glow">
          <CheckCircle2 className="w-10 h-10 text-emerald-400" />
        </div>

        <span className="text-[10px] font-mono uppercase tracking-widest px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold">
          TRANSMISSION CRYPTOGRAPHICALLY CONFIRMED
        </span>

        <h1 className="text-2xl md:text-3xl font-extrabold text-white mt-4">
          Tactical Deployment Dossier Dispatched
        </h1>

        <p className="text-xs text-slate-300 font-mono mt-3 leading-relaxed">
          Your sector clearance request has been cataloged under Transaction ID:
          <br />
          <strong className="text-cyan-400">TXN-IBVAP-2026-SECTOR-B-99182</strong>
        </p>

        <p className="text-xs text-slate-400 mt-4 leading-relaxed">
          The autonomous edge deployment suite and SHA-256 verification credentials will be transmitted to your defense liaison channel within 2 hours.
        </p>

        <button
          onClick={onReturnHome}
          className="mt-8 px-6 py-3 rounded-2xl bg-gradient-to-r from-emerald-500 via-cyan-500 to-blue-600 text-obsidian font-bold text-xs font-mono uppercase tracking-wider flex items-center justify-center space-x-2 mx-auto shadow-tactical-glow hover:brightness-110 transition-all group"
        >
          <Home className="w-4 h-4" />
          <span>Return to Command Post</span>
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  );
};
