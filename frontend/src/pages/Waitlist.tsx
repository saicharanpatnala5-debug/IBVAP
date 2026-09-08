import React from 'react';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { PricingTiers } from '../components/common/PricingTiers';
import { CTASection } from '../components/common/CTASection';
import { SEOHead } from '../components/common/SEOHead';

interface WaitlistProps {
  onSubmitted?: () => void;
}

export const Waitlist: React.FC<WaitlistProps> = ({ onSubmitted }) => {
  return (
    <div className="p-6 space-y-8 max-w-7xl mx-auto animate-fade-in">
      <SEOHead title="Procurement & Defense Deployment Tiers" description="Official procurement waitlist and deployment tiers for SIH 2026" />

      <Breadcrumbs items={[{ label: 'Procurement Tiers & Deployment Waitlist', isCurrent: true }]} />

      <PricingTiers />

      <CTASection onSubmitted={onSubmitted} />
    </div>
  );
};
