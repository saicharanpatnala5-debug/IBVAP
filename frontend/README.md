# IBVAP - Tactical Command Center Frontend

High-performance, futuristic command post interface for the **Intelligent Border Video Analytics Platform (IBVAP)**.
Engineered for Smart India Hackathon (SIH 2026) | Problem Statement: SIH26187 (SSB / Ministry of Home Affairs).

## Key Features & Visual Identity
- **Futuristic & Minimalist Aesthetic**: Dark defense palette (`#090d16`), liquid glass (`backdrop-blur-xl bg-slate-900/60`), harsh neon gradients, radial orbs.
- **16 Mission-Critical Pages**: Dashboard, Live Monitoring, Cameras, Alerts, Incidents, Incident Details, Video Search, Analytics, Map View, Settings, About, Contact, Waitlist, Thank You, Custom 404, Login.
- **Modular Component Library**:
  - `camera/`: CameraCard, CameraGrid, PTZControls.
  - `alerts/`: AlertList, AlertBadge, AlertDetailModal.
  - `incidents/`: IncidentTimeline, ExplainableAICard.
  - `video/`: LiveStreamPlayer, EvidencePlayback, HUDOverlay.
  - `maps/`: TacticalMap (Vector GIS with virtual fence polygons & coverage cones).
  - `charts/`: ThreatRadarChart, HourlyBreachChart, RiskDistributionChart.
  - `common/`: Navbar, Sidebar, Breadcrumbs, CookieConsent, PricingTiers (3 defense tiers), FeatureCards (3 in a row), BentoGrid, Testimonials, CTASection (CTA above fields), SEOHead.
- **Explainable AI Integration**: Transparent 5W threat breakdown (What, Who, Where, When, Why) with calibrated risk scoring.
- **Dual Runtime Deployment**:
  1. Standard **Vite + React + TS** application with Dockerfile.
  2. Standalone **zero-dependency interactive dashboard** in `public/index.html` and `index.html` accessible instantly in any modern web browser.
