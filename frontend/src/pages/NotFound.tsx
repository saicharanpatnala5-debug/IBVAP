import React from 'react';
import { SEOHead } from '../components/common/SEOHead';
import { AlertOctagon, ArrowRight, Home } from 'lucide-react';

interface NotFoundProps {
  onReturnHome: () => void;
}

export const NotFound: React.FC<NotFoundProps> = ({ onReturnHome }) => {
  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <SEOHead title="404 — Sector Restricted" description="Sector boundary coordinate not found" />

      <div className="max-w-lg w-full rounded-3xl p-8 liquid-glass border border-rose-500/40 text-center shadow-2xl animate-fade-in">
        <div className="w-16 h-16 rounded-3xl bg-rose-500/20 border border-rose-500/50 flex items-center justify-center mx-auto mb-4 shadow-[0_0_20px_rgba(244,63,94,0.4)]">
          <AlertOctagon className="w-10 h-10 text-rose-400 animate-pulse" />
        </div>

        <span className="text-[10px] font-mono uppercase tracking-widest px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30 font-bold">
          CODE 404 — ACCESS DENIED
        </span>

        <h1 className="text-2xl md:text-3xl font-extrabold text-white mt-4 font-mono">
          Sector Restricted / Coordinate Void
        </h1>

        <p className="text-xs text-slate-300 font-mono mt-3 leading-relaxed">
          The requested coordinate or tactical route lies outside authorized BOP Alpha boundary parameters. Access is logged in the permanent cryptographic audit trail.
        </p>

        <button
          onClick={onReturnHome}
          className="mt-8 px-6 py-3 rounded-2xl bg-gradient-to-r from-emerald-500 via-cyan-500 to-blue-600 text-obsidian font-bold text-xs font-mono uppercase tracking-wider flex items-center justify-center space-x-2 mx-auto shadow-tactical-glow hover:brightness-110 transition-all group"
        >
          <Home className="w-4 h-4" />
          <span>Fall Back to Command Post</span>
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  );
};
