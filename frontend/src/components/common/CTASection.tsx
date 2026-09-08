import React, { useState } from 'react';
import { Shield, ArrowRight, CheckCircle2, Lock } from 'lucide-react';

interface CTASectionProps {
  onSubmitted?: () => void;
}

export const CTASection: React.FC<CTASectionProps> = ({ onSubmitted }) => {
  const [outpostCode, setOutpostCode] = useState('');
  const [commanderEmail, setCommanderEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!outpostCode || !commanderEmail) return;
    setSubmitted(true);
    if (onSubmitted) onSubmitted();
  };

  return (
    <section className="relative my-12 mx-4 max-w-5xl md:mx-auto rounded-3xl p-8 md:p-12 overflow-hidden liquid-glass border border-emerald-500/40 shadow-2xl">
      <div className="absolute -top-32 -left-32 w-80 h-80 bg-emerald-500/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-32 -right-32 w-80 h-80 bg-cyan-500/15 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 text-center max-w-2xl mx-auto">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono mb-4">
          <Shield className="w-3.5 h-3.5" />
          <span>AUTONOMOUS BORDER DEFENSE PROTOCOL</span>
        </div>

        <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
          Initiate Tactical Edge Deployment
        </h2>
        
        <p className="text-slate-300 text-xs md:text-sm mt-3 leading-relaxed">
          It's not future theory — it's active software-defined surveillance ready for your border sector. Connect your existing RTSP cameras in under 15 minutes.
        </p>

        {submitted ? (
          <div className="mt-8 p-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/40 text-center animate-fade-in">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
            <h3 className="text-base font-bold text-white">Transmission Cryptographically Confirmed</h3>
            <p className="text-xs font-mono text-slate-300 mt-1">
              Sector Clearance Code dispatched to verified defense credentials.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-8">
            <div className="mb-6 flex justify-center">
              <button
                type="submit"
                className="px-8 py-3.5 rounded-2xl font-mono text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-emerald-500 via-cyan-500 to-blue-600 text-obsidian shadow-tactical-glow hover:brightness-110 transition-all flex items-center space-x-2 group"
              >
                <span>Authorize Deployment Dossier</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto">
              <input
                type="text"
                placeholder="Tactical Post ID (e.g. BOP-ALPHA)"
                value={outpostCode}
                onChange={(e) => setOutpostCode(e.target.value)}
                required
                className="px-4 py-3 rounded-xl bg-slate-900/80 border border-slate-700 text-xs text-white placeholder-slate-500 font-mono focus:outline-none focus:border-emerald-500"
              />
              <input
                type="email"
                placeholder="Commander Official Email"
                value={commanderEmail}
                onChange={(e) => setCommanderEmail(e.target.value)}
                required
                className="px-4 py-3 rounded-xl bg-slate-900/80 border border-slate-700 text-xs text-white placeholder-slate-500 font-mono focus:outline-none focus:border-emerald-500"
              />
            </div>
            
            <p className="text-[10px] font-mono text-slate-500 mt-3 flex items-center justify-center space-x-1">
              <Lock className="w-3 h-3" />
              <span>Zero-Trust 256-Bit Encrypted Liaison Channel</span>
            </p>
          </form>
        )}
      </div>
    </section>
  );
};
