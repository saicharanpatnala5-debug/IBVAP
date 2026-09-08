import React from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { TacticalMap } from '../components/maps/TacticalMap';
import { SEOHead } from '../components/common/SEOHead';
import { Map, Layers, Navigation } from 'lucide-react';

export const MapView: React.FC = () => {
  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto animate-fade-in">
      <SEOHead title="GIS Tactical Border Map" description="Full-screen vector geospatial map with virtual fencing" />

      <div className="flex items-center justify-between">
        <Breadcrumbs items={[{ label: 'Tactical GIS Map View', isCurrent: true }]} />
        <div className="flex items-center space-x-2">
          <button className="px-3 py-1.5 rounded-xl bg-slate-800 text-xs font-mono text-slate-300 flex items-center space-x-1">
            <Layers className="w-3.5 h-3.5" />
            <span>Virtual Fences</span>
          </button>
          <button className="px-3 py-1.5 rounded-xl bg-slate-800 text-xs font-mono text-slate-300 flex items-center space-x-1">
            <Navigation className="w-3.5 h-3.5" />
            <span>Camera Cones</span>
          </button>
        </div>
      </div>

      <TacticalMap />
    </div>
  );
};
