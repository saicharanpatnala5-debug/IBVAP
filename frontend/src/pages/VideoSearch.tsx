import React, { useState } from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { SEOHead } from '../components/common/SEOHead';
import { Search, Car, UserCheck, Calendar, Filter } from 'lucide-react';

export const VideoSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('DL01AB1234');
  const [category, setCategory] = useState<'ANPR' | 'FACE'>('ANPR');

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto animate-fade-in">
      <SEOHead title="ANPR & Biometric Forensic Search" description="Search license plates and face recognition sightings" />

      <Breadcrumbs items={[{ label: 'Forensic Video & Target Search', isCurrent: true }]} />

      {/* Search Header Bar */}
      <div className="rounded-3xl p-6 liquid-glass border border-slate-800 shadow-2xl">
        <div className="flex flex-col md:flex-row items-center gap-4">
          <div className="flex items-center space-x-2 bg-slate-900/80 p-1.5 rounded-xl border border-slate-800">
            <button
              onClick={() => setCategory('ANPR')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono flex items-center space-x-1.5 transition-colors ${
                category === 'ANPR' ? 'bg-emerald-500/20 text-emerald-400 font-bold' : 'text-slate-400'
              }`}
            >
              <Car className="w-3.5 h-3.5" />
              <span>Vehicle Plate (ANPR)</span>
            </button>
            <button
              onClick={() => setCategory('FACE')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono flex items-center space-x-1.5 transition-colors ${
                category === 'FACE' ? 'bg-emerald-500/20 text-emerald-400 font-bold' : 'text-slate-400'
              }`}
            >
              <UserCheck className="w-3.5 h-3.5" />
              <span>Facial Watchlist (YuNet)</span>
            </button>
          </div>

          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
            <input
              type="text"
              placeholder={category === 'ANPR' ? 'Enter Plate Number (e.g. DL01AB1234)...' : 'Enter Target Name or Code...'}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700 text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <button className="px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-obsidian font-bold text-xs font-mono shadow-tactical-glow">
            Execute Forensic Search
          </button>
        </div>
      </div>

      {/* Forensic Results */}
      <div className="space-y-3">
        <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">
          MATCHING TACTICAL SIGHTINGS (2 RECORDS)
        </h3>

        <div className="rounded-2xl p-4 liquid-glass border-l-4 border-rose-500">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-white font-bold">PLATE: DL01AB1234 (RECON SUV)</span>
            <span className="text-rose-400 font-bold">BLACKLISTED VEHICLE MATCH</span>
          </div>
          <p className="text-xs text-slate-300 mt-1 font-mono">
            Camera CAM-01 Approach Road | 2026-09-06 02:40:48 UTC | Confidence: 96.8%
          </p>
        </div>

        <div className="rounded-2xl p-4 liquid-glass border-l-4 border-emerald-500">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-white font-bold">PLATE: HR26DK4411 (LOGISTICS TRUCK)</span>
            <span className="text-emerald-400 font-bold">AUTHORIZED SECTOR TRANSIT</span>
          </div>
          <p className="text-xs text-slate-300 mt-1 font-mono">
            Camera CAM-02 Checkpoint | 2026-09-06 01:15:22 UTC | Confidence: 98.2%
          </p>
        </div>
      </div>
    </div>
  );
};
