import React, { useState } from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { SEOHead } from '../components/common/SEOHead';
import { Sliders, Save, Shield, HardDrive, Bell } from 'lucide-react';

export const Settings: React.FC = () => {
  const [zoneWeight, setZoneWeight] = useState(30);
  const [nightWeight, setNightWeight] = useState(15);
  const [inwardWeight, setInwardWeight] = useState(20);
  const [retentionDays, setRetentionDays] = useState(30);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto animate-fade-in">
      <SEOHead title="System & Risk Engine Weights" description="Calibrated risk weights and DPDP retention policies" />

      <Breadcrumbs items={[{ label: 'System Configuration & Weights', isCurrent: true }]} />

      <form onSubmit={handleSave} className="space-y-6">
        {/* Calibrated Risk Scoring Weights */}
        <div className="rounded-3xl p-6 liquid-glass border border-slate-800 shadow-2xl">
          <div className="flex items-center space-x-2 pb-4 border-b border-slate-800 mb-6">
            <Sliders className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold font-mono text-white uppercase">
              Calibrated Explainable Risk Engine Weights
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs font-mono">
            <div>
              <div className="flex justify-between mb-2 text-slate-300">
                <span>ZONE INTRUSION WEIGHT</span>
                <span className="text-emerald-400 font-bold">{zoneWeight} pts</span>
              </div>
              <input
                type="range"
                min={10}
                max={50}
                value={zoneWeight}
                onChange={(e) => setZoneWeight(Number(e.target.value))}
                className="w-full accent-emerald-500"
              />
            </div>

            <div>
              <div className="flex justify-between mb-2 text-slate-300">
                <span>NIGHT CONTEXT WEIGHT</span>
                <span className="text-emerald-400 font-bold">{nightWeight} pts</span>
              </div>
              <input
                type="range"
                min={5}
                max={30}
                value={nightWeight}
                onChange={(e) => setNightWeight(Number(e.target.value))}
                className="w-full accent-emerald-500"
              />
            </div>

            <div>
              <div className="flex justify-between mb-2 text-slate-300">
                <span>INWARD TRAJECTORY</span>
                <span className="text-emerald-400 font-bold">{inwardWeight} pts</span>
              </div>
              <input
                type="range"
                min={10}
                max={40}
                value={inwardWeight}
                onChange={(e) => setInwardWeight(Number(e.target.value))}
                className="w-full accent-emerald-500"
              />
            </div>
          </div>
        </div>

        {/* Data Sovereignty & DPDP Retention */}
        <div className="rounded-3xl p-6 liquid-glass border border-slate-800 shadow-2xl">
          <div className="flex items-center space-x-2 pb-4 border-b border-slate-800 mb-6">
            <HardDrive className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold font-mono text-white uppercase">
              Edge Storage Quotas & DPDP Act 2023 Retention
            </h3>
          </div>

          <div className="max-w-md text-xs font-mono">
            <div className="flex justify-between mb-2 text-slate-300">
              <span>EVIDENCE RETENTION PERIOD</span>
              <span className="text-cyan-400 font-bold">{retentionDays} Days</span>
            </div>
            <input
              type="range"
              min={7}
              max={90}
              value={retentionDays}
              onChange={(e) => setRetentionDays(Number(e.target.value))}
              className="w-full accent-cyan-500"
            />
            <p className="text-[10px] text-slate-500 mt-2">
              Auto-purges non-incident raw video while preserving cryptographic SHA-256 evidence seals.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <button
            type="submit"
            className="px-6 py-3 rounded-2xl bg-gradient-to-r from-emerald-500 via-cyan-500 to-blue-600 text-obsidian font-bold text-xs font-mono uppercase tracking-wider flex items-center space-x-2 shadow-tactical-glow hover:brightness-110 transition-all"
          >
            <Save className="w-4 h-4" />
            <span>Apply Tactical System Settings</span>
          </button>
          {saved && (
            <span className="text-xs font-mono text-emerald-400 font-bold animate-fade-in">
              [OK] Parameters Synchronized with Edge Nodes
            </span>
          )}
        </div>
      </form>
    </div>
  );
};
