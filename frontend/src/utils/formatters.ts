import { SeverityLevel } from '../types';

export function formatTimestamp(isoString?: string): string {
  if (!isoString) return '--:--:-- UTC';
  try {
    const d = new Date(isoString);
    return d.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
  } catch {
    return isoString;
  }
}

export function formatCoordinates(lat: number, lon: number): string {
  const latDir = lat >= 0 ? 'N' : 'S';
  const lonDir = lon >= 0 ? 'E' : 'W';
  return `${Math.abs(lat).toFixed(4)}° ${latDir}, ${Math.abs(lon).toFixed(4)}° ${lonDir}`;
}

export function getSeverityBadgeStyles(severity: SeverityLevel): {
  bg: string;
  text: string;
  border: string;
  glow: string;
} {
  switch (severity) {
    case 'CRITICAL':
      return {
        bg: 'bg-rose-500/20',
        text: 'text-rose-400',
        border: 'border-rose-500/50',
        glow: 'shadow-[0_0_15px_rgba(244,63,94,0.35)]',
      };
    case 'HIGH':
      return {
        bg: 'bg-orange-500/20',
        text: 'text-orange-400',
        border: 'border-orange-500/50',
        glow: 'shadow-[0_0_12px_rgba(249,115,22,0.3)]',
      };
    case 'MEDIUM':
      return {
        bg: 'bg-amber-500/20',
        text: 'text-amber-400',
        border: 'border-amber-500/50',
        glow: 'shadow-[0_0_10px_rgba(245,158,11,0.25)]',
      };
    case 'LOW':
      return {
        bg: 'bg-blue-500/20',
        text: 'text-blue-400',
        border: 'border-blue-500/50',
        glow: 'shadow-[0_0_8px_rgba(59,130,246,0.2)]',
      };
    case 'NORMAL':
    default:
      return {
        bg: 'bg-emerald-500/20',
        text: 'text-emerald-400',
        border: 'border-emerald-500/50',
        glow: 'shadow-[0_0_8px_rgba(16,185,129,0.2)]',
      };
  }
}

export function formatCurrencyINR(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatSeverityLabel(severity?: string): string {
  if (!severity) return 'Normal';
  const s = severity.toUpperCase();
  switch (s) {
    case 'CRITICAL':
      return 'Critical';
    case 'HIGH':
      return 'High';
    case 'MEDIUM':
      return 'Medium';
    case 'LOW':
      return 'Low';
    case 'NORMAL':
    default:
      return 'Normal';
  }
}

export function formatSensorType(type?: string): string {
  if (!type) return '4K Optical';
  const t = type.toUpperCase();
  switch (t) {
    case 'OPTICAL_4K':
      return '4K Optical';
    case 'THERMAL_LWIR':
      return 'Thermal LWIR';
    case 'RADAR_FMCW':
      return 'Radar FMCW';
    case 'ANPR_CAMERA':
      return 'ANPR Camera';
    case 'STARLIGHT_PTZ':
      return 'Starlight PTZ';
    case 'PTZ_TRACKER':
      return 'PTZ Tracker';
    case 'IR_NIGHT':
      return 'IR Night';
    default:
      return type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }
}

export function formatRuleTriggered(rule?: string): string {
  if (!rule) return 'Perimeter Protocol';
  const r = rule.toUpperCase();
  switch (r) {
    case 'CROSSING_DETECTED':
      return 'Perimeter Crossing';
    case 'LOITERING_ALERT':
    case 'LOITERING':
      return 'Loitering Detected';
    case 'DIRECTION_ANOMALY':
      return 'Wrong-Way Movement';
    case 'TAMPER_DETECTED':
      return 'Camera Tampering';
    case 'ZONE_BREACH':
      return 'Zone Breach';
    case 'ZONE_INTRUSION':
      return 'Zone Intrusion';
    case 'BREACH_DETECTED':
      return 'Breach Detected';
    default:
      return rule.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }
}
