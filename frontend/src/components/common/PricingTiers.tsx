import React from 'react';
import { Shield, ArrowRight } from 'lucide-react';

interface PricingTiersProps {
  onSelectTier?: (tierName: string) => void;
}

export const PricingTiers: React.FC<PricingTiersProps> = ({ onSelectTier }) => {
  const tiers = [
    {
      id: 'tier-outpost',
      name: 'Tactical Post',
      subtitle: 'Border Outpost (BOP) Autonomous Deployment',
      price: '₹4,50,000',
      period: '/ outpost node / yr',
      badge: 'BOP READY',
      isFeatured: false,
      description: 'Ruggedized standalone edge node intelligence for tactical outposts with intermittent backhaul.',
      features: [
        '✓ 4 Multi-spectral Camera RTSP Feeds',
        '✓ ByteTrack Edge Trajectory Correlation',
        '✓ Sub-20ms Zone Intrusion Detection',
        '✓ 30-Day Encrypted SQLite WAL Evidence Ring Buffer',
        '✓ Local Audible Alarm & Relay Triggering',
        '✓ 100% Air-Gapped Offline Operation'
      ],
      cta: 'Provision BOP Post Node'
    },
    {
      id: 'tier-sector',
      name: 'Sector HQ Battalion',
      subtitle: 'Command Center & Multi-Camera Fusion Hub',
      price: '₹18,50,000',
      period: '/ sector cluster / yr',
      badge: 'RECOMMENDED STRATEGIC',
      isFeatured: true,
      description: 'Complete multi-camera topology graph correlation with Indian ANPR, YuNet biometrics, and explainable AI.',
      features: [
        '✓ Up to 32 Distributed Optical / LWIR Thermal Feeds',
        '✓ Multi-Camera Directed Graph Re-ID Tracking',
        '✓ Indian ANPR & YuNet National Watchlist Match',
        '✓ Calibrated Explainable Risk Engine (5W Cards)',
        '✓ Real-time WebSockets Command Dashboard',
        '✓ Tamper-Evident SHA-256 Chain of Custody Audit Log',
        '✓ 24/7 Defense Engineering Support & Drone Integration'
      ],
      cta: 'Deploy Sector HQ Cluster'
    },
    {
      id: 'tier-sovereign',
      name: 'Sovereign Fleet Command',
      subtitle: 'National Strategic Border Infrastructure',
      price: 'Custom Sovereign',
      period: 'procurement quote',
      badge: 'ENTERPRISE DEFENSE',
      isFeatured: false,
      description: 'Distributed sovereign edge mesh across entire international borders with satellite / HF tactical sync.',
      features: [
        '✓ Unlimited Distributed Edge Compute Nodes',
        '✓ Multi-Corridor Strategic Cross-BOP Tracking',
        '✓ Hardware Security Module (HSM) Cryptography',
        '✓ Air-Gapped Custom Model Retraining Pipeline',
        '✓ GIS Defense Mapping & Drone Auto-Dispatch',
        '✓ Full Source Code Escrow & MoD Deployment Audits',
        '✓ Custom Satellite & Tactical Radio Mesh Protocol'
      ],
      cta: 'Request Sovereign Defense RFP'
    }
  ];

  return (
    <section className="py-12 px-4 max-w-7xl mx-auto">
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono mb-4">
          <Shield className="w-3.5 h-3.5" />
          <span>OFFICIAL PROCUREMENT TIERS — SIH 2026</span>
        </div>
        <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
          Tactical Border Surveillance Architecture
        </h2>
        <p className="text-slate-400 mt-3 text-sm md:text-base leading-relaxed">
          It's not commercial CCTV surveillance — it's autonomous tactical border dominance. Choose the deployment tier certified for your strategic sector.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {tiers.map((tier) => (
          <div
            key={tier.id}
            className={`relative rounded-3xl p-8 flex flex-col justify-between transition-all duration-300 ${
              tier.isFeatured
                ? 'liquid-glass-glow border-2 border-emerald-500/80 shadow-tactical-glow -translate-y-2'
                : 'liquid-glass border border-slate-800/80 hover:border-slate-700'
            }`}
          >
            {tier.badge && (
              <div className="absolute -top-3.5 left-8 px-3 py-1 rounded-full text-[10px] font-mono font-bold tracking-widest uppercase bg-gradient-to-r from-emerald-500 to-cyan-500 text-obsidian shadow-lg">
                {tier.badge}
              </div>
            )}

            <div>
              <div className="mb-4">
                <h3 className="text-xl font-bold text-white">{tier.name}</h3>
                <p className="text-xs font-mono text-slate-400 mt-1">{tier.subtitle}</p>
              </div>

              <div className="mb-6 flex items-baseline space-x-2">
                <span className="text-3xl font-extrabold text-slate-100 font-mono">{tier.price}</span>
                <span className="text-xs font-mono text-slate-400">{tier.period}</span>
              </div>

              <p className="text-xs text-slate-300 mb-6 leading-relaxed">
                {tier.description}
              </p>

              <div className="space-y-3 mb-8 border-t border-slate-800/80 pt-6">
                {tier.features.map((feat, idx) => (
                  <div key={idx} className="flex items-start space-x-2 text-xs text-slate-200">
                    <span className="text-emerald-400 font-bold flex-shrink-0">✓</span>
                    <span>{feat.replace('✓ ', '')}</span>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={() => onSelectTier && onSelectTier(tier.name)}
              className={`w-full py-3 px-4 rounded-2xl font-mono text-xs font-bold uppercase tracking-wider flex items-center justify-center space-x-2 transition-all group ${
                tier.isFeatured
                  ? 'bg-gradient-to-r from-emerald-500 via-cyan-500 to-blue-600 text-obsidian hover:shadow-tactical-glow hover:brightness-110'
                  : 'bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-slate-700'
              }`}
            >
              <span>{tier.cta}</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        ))}
      </div>
    </section>
  );
};
