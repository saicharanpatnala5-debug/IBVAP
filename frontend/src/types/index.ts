export type SeverityLevel = 'NORMAL' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type CameraStatus = 'ONLINE' | 'DEGRADED' | 'OFFLINE' | 'RECONNECTING';
export type SensorType = 'OPTICAL_4K' | 'THERMAL_LWIR' | 'ANPR_CAMERA' | 'STARLIGHT_PTZ';
export type ZoneType = 'RED_RESTRICTED' | 'YELLOW_MONITORING' | 'GREEN_NORMAL';
export type IncidentStatus = 'OPEN' | 'INVESTIGATING' | 'ESCALATED' | 'RESOLVED' | 'FALSE_POSITIVE';
export type UserRole = 'admin' | 'supervisor' | 'cctv_operator' | 'field_response' | 'auditor';

export interface Camera {
  camera_id: string;
  name: string;
  site: string;
  sector: string;
  latitude: number;
  longitude: number;
  stream_url: string;
  status: CameraStatus;
  fps: number;
  resolution: string;
  sensor_type?: SensorType;
  is_active: boolean;
  is_simulated?: boolean;
}

export interface CameraHealth {
  camera_id: string;
  fps: number;
  latency_ms: number;
  packet_loss_pct: number;
  frame_drops: number;
  ai_fps: number;
  status: 'HEALTHY' | 'WARNING' | 'CRITICAL';
  checked_at: string;
}

export interface Zone {
  zone_id: string;
  camera_id: string;
  name: string;
  zone_type: ZoneType;
  polygon_coords: [number, number][];
  alert_level: SeverityLevel;
  rules: {
    dwell_threshold?: number;
    direction?: string;
    speed_threshold?: number;
  };
}

export interface Alert {
  alert_id: string;
  event_id?: string;
  camera_id: string;
  zone_id?: string;
  incident_id?: string;
  severity: SeverityLevel;
  rule_triggered: string;
  message: string;
  risk_score: number;
  status: 'ACTIVE' | 'ACKNOWLEDGED' | 'DISMISSED';
  is_acknowledged?: boolean;
  acknowledged_by?: string;
  acknowledged_at?: string;
  created_at: string;
  snapshot_url?: string;
  confidence?: number;
  contributing_factors?: string[];
}

export interface ExplainableFactor {
  factor: string;
  weight: number;
  contribution: string;
}

export interface Incident {
  incident_id: string;
  title: string;
  description: string;
  severity: SeverityLevel;
  risk_score: number;
  status: IncidentStatus;
  primary_camera_id: string;
  associated_cameras: string[];
  zones_involved: string[];
  track_ids: string[];
  explainable_breakdown: {
    what: string;
    who: string;
    where: string;
    when: string;
    why: ExplainableFactor[];
  };
  evidence_snapshot_path?: string;
  created_at: string;
  updated_at: string;
}

export interface VehiclePlate {
  plate_number: string;
  camera_id: string;
  confidence: number;
  is_flagged: boolean;
  vehicle_type: string;
  timestamp: string;
}

export interface FaceSighting {
  sighting_id: string;
  camera_id: string;
  watchlist_match_name?: string;
  confidence: number;
  is_watchlist_hit: boolean;
  timestamp: string;
}

export interface AuditLog {
  log_id: string;
  timestamp: string;
  user_id: string;
  action: string;
  target_resource: string;
  details: string;
  sha256_hash: string;
}

export interface UserSession {
  user_id: string;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  token: string;
}

export interface PricingTier {
  id: string;
  name: string;
  tierSubtitle: string;
  priceINR: string;
  billingFrequency: string;
  badge?: string;
  isFeatured?: boolean;
  description: string;
  features: string[];
  ctaLabel: string;
}

export type DetectionClass = 'person' | 'vehicle' | 'object' | 'animal';

export type DetectionThreatLevel = 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW' | 'FILTERED_NON_THREAT';

export interface TacticalDetection {
  id: string;
  track_id: string;
  class_name: DetectionClass;
  label: string;
  sub_label?: string;
  confidence: number;
  // Normalized bounding box [x, y, width, height] (0.0 to 1.0)
  bbox: [number, number, number, number];
  threat_level: DetectionThreatLevel;
  color: string;
  details?: {
    vehicle_type?: string;
    posture?: string;
    speed_kmh?: number;
    anpr_plate?: string;
    anpr_norm?: string;
    anpr_status?: string;
    anpr_confidence?: number;
    owner_lookup_url?: string;
    payload_type?: string;
    species?: string;
    is_filtered_false_alarm?: boolean;
    distance_m?: number;
    behavior?: string;
    thermal_delta_c?: string;
  };
}


export interface DetectionTelemetry {
  personCount: number;
  vehicleCount: number;
  heavyVehicleCount?: number;
  objectCount: number;
  animalCount: number;
  totalActive: number;
  filteredFalseAlarms: number;
  highestThreat: DetectionThreatLevel;
}

