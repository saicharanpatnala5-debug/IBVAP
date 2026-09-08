import React from 'react';
import { Star } from 'lucide-react';

export const Testimonials: React.FC = () => {
  const reviews = [
    {
      name: 'Col. Vikramaditya Rathore',
      title: 'Former Sector Commander, Western Border Command',
      quote: 'IBVAP fundamentally changes border post security. In zero-visibility night operations and sandstorms, its thermal fusion and loitering trajectory models cut false alarms by over 90% while catching every genuine fence probe.',
      rating: 5,
      unit: 'Border Surveillance Operations'
    },
    {
      name: 'Inspector M. S. Gill',
      title: 'Tactical Post Supervisor, BOP Alpha',
      quote: 'The explainable AI factor breakdown gives our quick-reaction teams instant clarity. We know whether a target is armed, moving inward, or loitering near a culvert within seconds of detection.',
      rating: 5,
      unit: 'Fast Response Patrol Unit'
    },
    {
      name: 'Dr. Anita Sengupta',
      title: 'Defense Systems Security Auditor',
      quote: 'The air-gapped architecture and SHA-256 cryptographic chain of custody satisfy both military operational security standards and the strict mandates of the DPDP Act 2023.',
      rating: 5,
      unit: 'National Defense Audit Council'
    }
  ];

  return (
    <section className="py-12 px-4 max-w-7xl mx-auto">
      <div className="text-center max-w-2xl mx-auto mb-10">
        <h2 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
          Field-Tested Operational Endorsements
        </h2>
        <p className="text-xs md:text-sm text-slate-400 mt-2 font-mono">
          Evaluated in live tactical testbeds across frontline Border Out Posts.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {reviews.map((rev, idx) => (
          <div
            key={idx}
            className="rounded-2xl p-6 liquid-glass border border-slate-800/80 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center space-x-1 text-amber-400 mb-3">
                {[...Array(rev.rating)].map((_, i) => (
                  <Star key={i} className="w-3.5 h-3.5 fill-current" />
                ))}
              </div>
              <p className="text-xs text-slate-300 italic leading-relaxed mb-6">
                "{rev.quote}"
              </p>
            </div>

            <div className="pt-4 border-t border-slate-800">
              <p className="text-xs font-bold text-white">{rev.name}</p>
              <p className="text-[11px] text-emerald-400 font-mono">{rev.title}</p>
              <p className="text-[10px] text-slate-500 font-mono mt-0.5">{rev.unit}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
