import React, { useState } from 'react';
import { Shield, Lock, User, Key, ArrowRight, ShieldCheck } from 'lucide-react';
import { TacticalAuth } from '../services/auth';
import { SEOHead } from '../components/common/SEOHead';

interface LoginProps {
  onLoginSuccess: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('Admin@2026!');
  const [selectedPreset, setSelectedPreset] = useState('admin');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    const session = TacticalAuth.getDefaultPreset(selectedPreset);
    TacticalAuth.setSession(session);
    onLoginSuccess();
  };

  const applyPreset = (preset: string) => {
    setSelectedPreset(preset);
    if (preset === 'admin') {
      setUsername('admin');
      setPassword('Admin@2026!');
    } else if (preset === 'supervisor') {
      setUsername('supervisor');
      setPassword('Supervisor@2026!');
    } else {
      setUsername('operator_sharma');
      setPassword('Operator@2026!');
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 bg-obsidian reticle-grid relative overflow-hidden">
      <SEOHead title="Tactical Post Authentication" description="Login to IBVAP Command Post" />

      {/* Radial Orbs */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-emerald-500/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-cyan-500/15 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md rounded-3xl p-8 liquid-glass border border-slate-700 shadow-2xl relative z-10">
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 border border-emerald-500/40 flex items-center justify-center mx-auto mb-3 shadow-tactical-glow">
            <Shield className="w-8 h-8 text-emerald-400 animate-pulse-slow" />
          </div>
          <h1 className="text-xl font-extrabold text-white tracking-wider font-mono">
            IBVAP COMMAND POST
          </h1>
          <p className="text-xs font-mono text-slate-400 mt-1">
            BOP Alpha — Sector B Tactical Clearance
          </p>
        </div>

        {/* RBAC Preset Quick Select */}
        <div className="mb-6">
          <p className="text-[10px] font-mono uppercase text-slate-400 font-bold mb-2">
            Select Clearance Preset:
          </p>
          <div className="grid grid-cols-3 gap-2">
            {[
              { id: 'admin', label: 'Commandant' },
              { id: 'supervisor', label: 'Supervisor' },
              { id: 'operator', label: 'Operator' },
            ].map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => applyPreset(p.id)}
                className={`py-1.5 px-2 rounded-xl text-xs font-mono transition-all ${
                  selectedPreset === p.id
                    ? 'bg-emerald-500/20 border border-emerald-500/60 text-emerald-300 font-bold shadow-tactical-glow'
                    : 'bg-slate-800/60 border border-slate-700 text-slate-400 hover:text-white'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-mono text-slate-300 mb-1.5">
              MILITARY USERNAME
            </label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-500 absolute left-3 top-3.5" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono text-slate-300 mb-1.5">
              TACTICAL ACCESS KEY
            </label>
            <div className="relative">
              <Key className="w-4 h-4 text-slate-500 absolute left-3 top-3.5" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full mt-6 py-3 px-4 rounded-2xl font-mono text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-emerald-500 via-cyan-500 to-blue-600 text-obsidian shadow-tactical-glow hover:brightness-110 transition-all flex items-center justify-center space-x-2 group"
          >
            <span>Authenticate Sector Clearance</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </form>

        <div className="mt-6 pt-4 border-t border-slate-800 text-center text-[10px] font-mono text-slate-500 flex items-center justify-center space-x-1">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Air-Gapped Local Verification | SIH 2026</span>
        </div>
      </div>
    </div>
  );
};
