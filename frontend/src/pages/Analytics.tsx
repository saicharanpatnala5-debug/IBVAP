import React from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { ThreatRadarChart } from '../components/charts/ThreatRadarChart';
import { HourlyBreachChart } from '../components/charts/HourlyBreachChart';
import { RiskDistributionChart } from '../components/charts/RiskDistributionChart';
import { SEOHead } from '../components/common/SEOHead';
import { BarChart3, TrendingDown, Clock, ShieldCheck } from 'lucide-react';

export const Analytics: React.FC = () => {
  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto animate-fade-in">
      <SEOHead title="Defense Posture & Threat Analytics" description="Tactical border defense intelligence and incident trends" />

      <Breadcrumbs items={[{ label: 'Executive Threat Analytics', isCurrent: true }]} />

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="rounded-2xl p-6 liquid-glass border border-slate-800">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>FALSE ALARM REDUCTION</span>
            <TrendingDown className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-3xl font-extrabold font-mono text-emerald-400 mt-2">-92.4%</p>
          <p className="text-xs text-slate-400 mt-1">Multi-frame trajectory confirmation filtering</p>
        </div>

        <div className="rounded-2xl p-6 liquid-glass border border-slate-800">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>MEAN RESPONSE TIME (MRT)</span>
            <Clock className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-3xl font-extrabold font-mono text-cyan-400 mt-2">18.2 sec</p>
          <p className="text-xs text-slate-400 mt-1">From edge intrusion to operator acknowledgment</p>
        </div>

        <div className="rounded-2xl p-6 liquid-glass border border-slate-800">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>CHAIN OF CUSTODY VERIFIED</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-3xl font-extrabold font-mono text-white mt-2">100.0%</p>
          <p className="text-xs text-slate-400 mt-1">Zero cryptographic tampering violations</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <HourlyBreachChart />
        <ThreatRadarChart />
      </div>

      <RiskDistributionChart />
    </div>
  );
};
