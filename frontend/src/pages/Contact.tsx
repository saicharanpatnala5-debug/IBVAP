import React, { useState } from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { SEOHead } from '../components/common/SEOHead';
import { Mail, Shield, Send, CheckCircle2, Key } from 'lucide-react';

export const Contact: React.FC = () => {
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    designation: '',
    sector: '',
    message: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto animate-fade-in">
      <SEOHead title="Secure Tactical Dispatch Contact" description="Encrypted military liaison and command dispatch inquiries" />

      <Breadcrumbs items={[{ label: 'Secure Tactical Liaison', isCurrent: true }]} />

      <div className="rounded-3xl p-8 liquid-glass border border-slate-800 shadow-2xl">
        <div className="flex items-center space-x-3 pb-6 border-b border-slate-800 mb-6">
          <div className="p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/40 text-emerald-400">
            <Mail className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Encrypted Command Liaison Dispatch</h2>
            <p className="text-xs font-mono text-slate-400 mt-0.5">
              Secure Communications for Defense Outpost Commanders & MoD Evaluators
            </p>
          </div>
        </div>

        {submitted ? (
          <div className="py-12 text-center animate-fade-in">
            <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-white">Transmission Cryptographically Registered</h3>
            <p className="text-xs font-mono text-slate-400 mt-1 max-w-md mx-auto">
              Your inquiry has been encrypted with the IBVAP Sector Public Key and queued for priority tactical response.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4 text-xs font-mono">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-300 mb-1.5">OFFICER / EVALUATOR NAME</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Commandant S. R. Joshi"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="block text-slate-300 mb-1.5">TACTICAL DESIGNATION & POST</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. BOP-Alpha Sector Commander"
                  value={formData.designation}
                  onChange={(e) => setFormData({ ...formData, designation: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-300 mb-1.5">OPERATIONAL SECTOR CODE</label>
              <input
                type="text"
                required
                placeholder="e.g. SECTOR-B-ALPHA-90"
                value={formData.sector}
                onChange={(e) => setFormData({ ...formData, sector: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-slate-300 mb-1.5">DISPATCH TRANSMISSION DETAILS</label>
              <textarea
                rows={4}
                required
                placeholder="Detail technical requirements, camera fleet specifications, or field evaluation schedule..."
                value={formData.message}
                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            <button
              type="submit"
              className="px-6 py-3 rounded-2xl bg-gradient-to-r from-emerald-500 via-cyan-500 to-blue-600 text-obsidian font-bold text-xs font-mono uppercase tracking-wider flex items-center space-x-2 shadow-tactical-glow hover:brightness-110 transition-all"
            >
              <Send className="w-4 h-4" />
              <span>Transmit Encrypted Dispatch</span>
            </button>
          </form>
        )}

        <div className="mt-8 pt-4 border-t border-slate-800 flex items-center justify-between text-[10px] font-mono text-slate-500">
          <span className="flex items-center space-x-1">
            <Key className="w-3 h-3 text-cyan-400" />
            <span>PGP Fingerprint: 4F92 B7A1 9902 C1D8 E5A7</span>
          </span>
          <span>Zero-Trust MoD Compliant</span>
        </div>
      </div>
    </div>
  );
};
