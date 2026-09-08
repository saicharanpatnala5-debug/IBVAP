import React from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { FeatureCards } from '../components/common/FeatureCards';
import { Testimonials } from '../components/common/Testimonials';
import { SEOHead } from '../components/common/SEOHead';
import { BenefitsSection } from '../components/BenefitsSection';
import { Shield, Target, Cpu, Eye, Lock, CheckCircle2 } from 'lucide-react';

export const About: React.FC = () => {
  return (
    <div className="p-6 space-y-12 max-w-7xl mx-auto animate-fade-in">
      <SEOHead title="Mission & Sovereign Defense Architecture" description="Autonomous border video intelligence platform" />

      <Breadcrumbs items={[{ label: 'Mission & Platform Briefing', isCurrent: true }]} />

      {/* Hero Section */}
      <div className="text-center max-w-3xl mx-auto">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono mb-4">
          <Shield className="w-3.5 h-3.5" />
          <span>SMART INDIA HACKATHON 2026 | SIH26187</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight leading-tight">
          AI-Assisted Border Video Analytics Platform
        </h1>
        <p className="text-emerald-400 font-mono text-sm mt-3 font-semibold">
          It's not passive CCTV monitoring — it's proactive AI-assisted border dominance.
        </p>
        <p className="text-slate-300 text-sm md:text-base mt-4 leading-relaxed">
          IBVAP transforms frontline legacy security cameras into intelligent, zero-trust edge surveillance grids. By fusing optical 4K and thermal LWIR feeds with topological graph tracking, Indian ANPR, and calibrated 5W explainable AI, IBVAP empowers border forces with instant threat interception.
        </p>
      </div>

      {/* 3 Strategic Pillars */}
      <FeatureCards />

      {/* Key Benefits Section */}
      <div className="rounded-3xl overflow-hidden border border-neutral-800 shadow-2xl bg-black">
        <BenefitsSection />
      </div>

      {/* Core Tenets with Checkmarks */}
      <div className="rounded-3xl p-8 liquid-glass border border-slate-800 shadow-2xl">
        <h3 className="text-xl font-bold text-white mb-6 text-center">
          Sovereign Defense Engineering Mandates
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-slate-300">
          <div className="space-y-3">
            <div className="flex items-start space-x-2">
              <span className="text-emerald-400 font-bold">✓</span>
              <span>100% Air-Gapped Operation — zero public internet or cloud backhaul required.</span>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-emerald-400 font-bold">✓</span>
              <span>Explainable AI Cards — full transparency on risk factors with mathematical weights.</span>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-emerald-400 font-bold">✓</span>
              <span>Multi-Camera Re-ID Graph — tracks intruders across blind zones and tactical corridors.</span>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-start space-x-2">
              <span className="text-emerald-400 font-bold">✓</span>
              <span>SHA-256 Tamper Seals — court-admissible forensic evidence chain of custody.</span>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-emerald-400 font-bold">✓</span>
              <span>DPDP Act 2023 Compliance — automated edge ring-buffer quotas and privacy audits.</span>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-emerald-400 font-bold">✓</span>
              <span>Multi-Spectral Night Vision — Retinex contrast enhancement for zero-lux breaches.</span>
            </div>
          </div>
        </div>
      </div>

      <Testimonials />
    </div>
  );
};
