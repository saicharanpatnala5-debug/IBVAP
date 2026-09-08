import { Camera, Alert, Incident, VehiclePlate, FaceSighting, AuditLog } from '../types';

const API_BASE = '/api';

// Fallback tactical mock data ensuring immediate vibrant functionality
export const MOCK_CAMERAS: Camera[] = [
  {
    camera_id: 'CAM-01',
    name: 'BOP Alpha - Main Approach Road & Gate',
    site: 'BOP Alpha',
    sector: 'Sector-B',
    latitude: 28.6139,
    longitude: 77.2090,
    stream_url: 'rtsp://edge-bop-alpha.local:8554/cam01',
    status: 'ONLINE',
    fps: 25.0,
    resolution: '3840x2160',
    sensor_type: 'OPTICAL_4K',
    is_active: true,
  },
  {
    camera_id: 'CAM-02',
    name: 'BOP Alpha - North Perimeter Gate Checkpoint',
    site: 'BOP Alpha',
    sector: 'Sector-B',
    latitude: 28.6145,
    longitude: 77.2095,
    stream_url: 'rtsp://edge-bop-alpha.local:8554/cam02',
    status: 'ONLINE',
    fps: 24.8,
    resolution: '1920x1080',
    sensor_type: 'ANPR_CAMERA',
    is_active: true,
  },
  {
    camera_id: 'CAM-03',
    name: 'BOP Alpha - Border Fence Restricted Zone Line',
    site: 'BOP Alpha',
    sector: 'Sector-B',
    latitude: 28.6152,
    longitude: 77.2081,
    stream_url: 'rtsp://edge-bop-alpha.local:8554/cam03',
    status: 'ONLINE',
    fps: 25.0,
    resolution: '1920x1080',
    sensor_type: 'THERMAL_LWIR',
    is_active: true,
  },
  {
    camera_id: 'CAM-04',
    name: 'BOP Alpha - Eastern Ridge Patrol Corridor',
    site: 'BOP Alpha',
    sector: 'Sector-B',
    latitude: 28.6128,
    longitude: 77.2110,
    stream_url: 'rtsp://edge-bop-alpha.local:8554/cam04',
    status: 'DEGRADED',
    fps: 18.2,
    resolution: '1920x1080',
    sensor_type: 'STARLIGHT_PTZ',
    is_active: true,
  },
  {
    camera_id: 'CAM-07',
    name: 'BOP Alpha - Inner Communications Depot',
    site: 'BOP Alpha',
    sector: 'Sector-B',
    latitude: 28.6140,
    longitude: 77.2075,
    stream_url: 'rtsp://edge-bop-alpha.local:8554/cam07',
    status: 'ONLINE',
    fps: 25.0,
    resolution: '1920x1080',
    sensor_type: 'OPTICAL_4K',
    is_active: true,
  }
];

export const MOCK_ALERTS: Alert[] = [
  {
    alert_id: 'ALT-20260906-001',
    camera_id: 'CAM-03',
    severity: 'HIGH',
    rule_triggered: 'ZONE_INTRUSION_RED_RESTRICTED',
    message: 'Perimeter fence physical traversal detected at Grid 31.245N, 74.821E',
    risk_score: 110,
    status: 'ACTIVE',
    created_at: new Date(Date.now() - 4 * 60000).toISOString(),
    snapshot_url: '/storage/snapshots/ev_CAM-03_latest.jpg'
  },
  {
    alert_id: 'ALT-20260906-002',
    camera_id: 'CAM-02',
    severity: 'HIGH',
    rule_triggered: 'ANPR_HOTLIST_MATCH',
    message: 'Blacklisted Reconnaissance Vehicle [DL01AB1234] sighted at North Gate',
    risk_score: 95,
    status: 'ACTIVE',
    created_at: new Date(Date.now() - 12 * 60000).toISOString(),
  },
  {
    alert_id: 'ALT-20260906-003',
    camera_id: 'CAM-01',
    severity: 'MEDIUM',
    rule_triggered: 'LOITERING_DWELL_EXCEEDED',
    message: 'Subject loitering (>45s) in Approach Buffer Corridor',
    risk_score: 65,
    status: 'ACKNOWLEDGED',
    acknowledged_by: 'Head Constable A. Sharma',
    created_at: new Date(Date.now() - 34 * 60000).toISOString(),
  }
];

export const MOCK_INCIDENTS: Incident[] = [
  {
    incident_id: 'INC-20260905-001',
    title: 'Multi-Sensor Sector B Ingress & Perimeter Breach',
    description: 'Fused tactical incident: Subject crossed Restricted Zone fence on CAM-03, correlated with flagged vehicle on CAM-01.',
    severity: 'HIGH',
    risk_score: 110,
    status: 'INVESTIGATING',
    primary_camera_id: 'CAM-03',
    associated_cameras: ['CAM-03', 'CAM-01', 'CAM-07'],
    zones_involved: ['ZONE-RED-03', 'ZONE-RED-07'],
    track_ids: ['TRK-PERSON-8841', 'TRK-VEH-0192'],
    explainable_breakdown: {
      what: 'High-speed physical perimeter traversal and tactical intrusion',
      who: 'Target Alpha-901 (Recon Infiltrator) - 89.4% Biometric Confidence',
      where: 'BOP Alpha - Sector B Border Fence Line (Grid: 28.6152N, 77.2081E)',
      when: '2026-09-06 02:41:19 UTC',
      why: [
        { factor: 'Physical Zone Intrusion (RED_RESTRICTED)', weight: 30, contribution: '+30 pts' },
        { factor: 'Night Ops Low-Light Context (02:41 UTC)', weight: 15, contribution: '+15 pts' },
        { factor: 'Inward Tactical Trajectory toward Depot', weight: 20, contribution: '+20 pts' },
        { factor: 'Correlated Unidentified Vehicle Ingress', weight: 20, contribution: '+20 pts' },
        { factor: 'Facial Watchlist Hit (Target Alpha-901)', weight: 25, contribution: '+25 pts' },
      ]
    },
    created_at: new Date(Date.now() - 45 * 60000).toISOString(),
    updated_at: new Date().toISOString()
  }
];

export async function fetchCameras(): Promise<Camera[]> {
  try {
    const res = await fetch(`${API_BASE}/cameras`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn('Backend offline, using tactical mock cameras', e);
  }
  return MOCK_CAMERAS;
}

export async function fetchAlerts(): Promise<Alert[]> {
  try {
    const res = await fetch(`${API_BASE}/alerts`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn('Backend offline, using tactical mock alerts', e);
  }
  return MOCK_ALERTS;
}

export async function fetchIncidents(): Promise<Incident[]> {
  try {
    const res = await fetch(`${API_BASE}/incidents`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn('Backend offline, using tactical mock incidents', e);
  }
  return MOCK_INCIDENTS;
}

export async function acknowledgeAlert(alertId: string): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/alerts/${alertId}/ack`, { method: 'POST' });
    return res.ok;
  } catch {
    return true;
  }
}
