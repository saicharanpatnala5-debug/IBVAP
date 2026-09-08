/**
 * IBVAP - Explainable Multi-Factor Risk Scoring Engine
 * Directly implements PRD Section 12 & Section 5.6 (FR-06)
 * Severity Scale: 0 to 120+
 * 0-29: NORMAL | 30-59: LOW | 60-89: MEDIUM | 90-119: HIGH | 120+: CRITICAL
 */

export interface RiskFactor {
  factor: string;
  points: number;
  confidence: number;
  explanation: string;
  trigger_rule: string;
}

export interface RiskEvaluationResult {
  totalScore: number;
  severity: 'NORMAL' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  isCriticalSpike: boolean;
  contributingFactors: RiskFactor[];
  summaryRule: string;
}

export interface RiskContextInput {
  isZoneIntrusion?: boolean;
  isNightTime?: boolean;
  isLoitering?: boolean;
  isInwardMovement?: boolean;
  isWatchlistHit?: boolean;
  hasMultiSignalCorrelation?: boolean;
  baseDetectionsCount?: number;
}

export const RISK_WEIGHTS = {
  ZONE_INTRUSION: 30,       // Restricted Red Zone Breach (+30 pts)
  NIGHT_CONTEXT: 15,        // 20:00 to 05:30 IST Low Visibility (+15 pts)
  LOITERING: 15,            // Centroid dwell > 15s (+15 pts)
  INWARD_VELOCITY: 20,      // Trajectory vector toward India > 1.2 m/s (+20 pts)
  WATCHLIST_HIT: 35,        // ANPR or Biometric Watchlist (+35 pts)
  MULTI_SIGNAL: 10,         // Correlated across 2+ sensors (+10 pts)
};

export function evaluateRisk(input: RiskContextInput): RiskEvaluationResult {
  let totalScore = 0;
  const factors: RiskFactor[] = [];
  const rulesTriggered: string[] = [];

  if (input.isZoneIntrusion) {
    totalScore += RISK_WEIGHTS.ZONE_INTRUSION;
    factors.push({
      factor: 'Restricted Zone Intrusion',
      points: RISK_WEIGHTS.ZONE_INTRUSION,
      confidence: 0.96,
      explanation: 'Target centroid intersects RED_RESTRICTED virtual polygon.',
      trigger_rule: 'RULE: PIP_POLYGON_BREACH'
    });
    rulesTriggered.push('Red Zone Breach');
  }

  if (input.isNightTime) {
    totalScore += RISK_WEIGHTS.NIGHT_CONTEXT;
    factors.push({
      factor: 'Nighttime Operational Context',
      points: RISK_WEIGHTS.NIGHT_CONTEXT,
      confidence: 0.98,
      explanation: 'Detection occurred during low-visibility darkness window (20:00 - 05:30 IST).',
      trigger_rule: 'RULE: NIGHT_OPS_WINDOW'
    });
    rulesTriggered.push('Night Window');
  }

  if (input.isLoitering) {
    totalScore += RISK_WEIGHTS.LOITERING;
    factors.push({
      factor: 'Suspicious Perimeter Loitering',
      points: RISK_WEIGHTS.LOITERING,
      confidence: 0.92,
      explanation: 'Target dwell time in buffer zone exceeded 15.0 seconds.',
      trigger_rule: 'RULE: DWELL_TIME_EXCEEDED'
    });
    rulesTriggered.push('Loitering');
  }

  if (input.isInwardMovement) {
    totalScore += RISK_WEIGHTS.INWARD_VELOCITY;
    factors.push({
      factor: 'Inward Penetration Vector',
      points: RISK_WEIGHTS.INWARD_VELOCITY,
      confidence: 0.89,
      explanation: 'Trajectory vector directed inward toward Indian territory (> 1.2 m/s).',
      trigger_rule: 'RULE: INWARD_BEARING_VECTOR'
    });
    rulesTriggered.push('Inward Velocity');
  }

  if (input.isWatchlistHit) {
    totalScore += RISK_WEIGHTS.WATCHLIST_HIT;
    factors.push({
      factor: 'Intelligence Watchlist Match',
      points: RISK_WEIGHTS.WATCHLIST_HIT,
      confidence: 0.94,
      explanation: 'Target matches ANPR hotlist or biometric person-of-interest database.',
      trigger_rule: 'RULE: NATIONAL_WATCHLIST_HIT'
    });
    rulesTriggered.push('Watchlist Match');
  }

  if (input.hasMultiSignalCorrelation) {
    totalScore += RISK_WEIGHTS.MULTI_SIGNAL;
    factors.push({
      factor: 'Multi-Sensor Optical/LWIR Cross-Correlation',
      points: RISK_WEIGHTS.MULTI_SIGNAL,
      confidence: 0.97,
      explanation: 'Simultaneous spatial confirmation across optical and thermal sensors.',
      trigger_rule: 'RULE: SENSOR_FUSION_MATCH'
    });
    rulesTriggered.push('Sensor Fusion');
  }

  // Determine Severity Tier (PRD Section 5.6 & 12)
  let severity: RiskEvaluationResult['severity'] = 'NORMAL';
  if (totalScore >= 120) {
    severity = 'CRITICAL';
  } else if (totalScore >= 90) {
    severity = 'HIGH';
  } else if (totalScore >= 60) {
    severity = 'MEDIUM';
  } else if (totalScore >= 30) {
    severity = 'LOW';
  }

  return {
    totalScore,
    severity,
    isCriticalSpike: totalScore >= 90,
    contributingFactors: factors,
    summaryRule: rulesTriggered.length > 0 
      ? `Rule: ${rulesTriggered.join(' + ')}` 
      : 'Rule: Standard Spatial Baseline Monitoring'
  };
}
