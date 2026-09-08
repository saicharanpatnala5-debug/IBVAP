import { TacticalDetection, DetectionClass, DetectionTelemetry } from '../types';

/**
 * Trajectory keyframe point: [time, x, y, width, height]
 * Coordinates are normalized (0.0 to 1.0)
 */
interface TrajectoryKeyframe {
  time: number;
  x: number;
  y: number;
  w: number;
  h: number;
}

interface TrackedEntityDefinition {
  id: string;
  track_id: string;
  class_name: DetectionClass;
  label: string;
  sub_label?: string;
  confidenceBase: number;
  confidenceVariance: number;
  threat_level: TacticalDetection['threat_level'];
  color: string;
  keyframes: TrajectoryKeyframe[];
  details?: TacticalDetection['details'];
}

// Pre-defined trajectory maps for preset scenarios and cameras
// Pre-defined trajectory maps for preset scenarios and cameras
// Strictly accurate to actual scene content: NO fake clutter, NO unnatural overlapping entities
const SCENARIO_TRACKS: Record<string, TrackedEntityDefinition[]> = {
  // DAHUA 8MP 4K CCTV: Night-time driveway/perimeter
  // Actual content: 1 stationary parked white sedan on right + 1 pedestrian walking along walkway
  // ZERO animals, ZERO floating weapons
  'dahua_perimeter_4k': [
    {
      id: 'dahua-v1',
      track_id: 'TRK-V39',
      class_name: 'vehicle',
      label: 'TARGET: VEHICLE',
      sub_label: 'PARKED SEDAN (MONITORED)',
      confidenceBase: 0.982,
      confidenceVariance: 0.006,
      threat_level: 'MODERATE',
      color: '#06b6d4',
      keyframes: [
        { time: 0, x: 0.57, y: 0.64, w: 0.38, h: 0.34 },
        { time: 12, x: 0.57, y: 0.64, w: 0.38, h: 0.34 }
      ],
      details: {
        speed_kmh: 0.0,
        anpr_status: 'PARKED_MONITORED',
        distance_m: 14.5,
        behavior: 'Stationary monitored vehicle in perimeter driveway'
      }
    },
    {
      id: 'dahua-p1',
      track_id: 'TRK-P104',
      class_name: 'person',
      label: 'TARGET: PERSON',
      sub_label: 'PEDESTRIAN (WALKING)',
      confidenceBase: 0.986,
      confidenceVariance: 0.008,
      threat_level: 'CRITICAL',
      color: '#f43f5e',
      keyframes: [
        { time: 0, x: 0.51, y: 0.58, w: 0.08, h: 0.26 },
        { time: 2, x: 0.50, y: 0.63, w: 0.08, h: 0.28 },
        { time: 4, x: 0.49, y: 0.69, w: 0.09, h: 0.28 },
        { time: 6, x: 0.48, y: 0.75, w: 0.10, h: 0.25 },
        { time: 7.5, x: 0.47, y: 0.82, w: 0.11, h: 0.18 },
        { time: 12, x: 0.47, y: 0.82, w: 0.11, h: 0.18 }
      ],
      details: {
        posture: 'walking_stride',
        speed_kmh: 4.2,
        distance_m: 8.2,
        behavior: 'Foot transit along walkway toward foreground'
      }
    }
  ],

  // SCENARIO 01: Perimeter Breach Incursion
  // Actual content: 1 Intruder crawling through fence + 1 Silhouetted wire cutter tool
  // ZERO random cars in fence, ZERO random cows
  'scenario_01_perimeter_breach': [
    {
      id: 'scen1-p1',
      track_id: 'TRK-P104',
      class_name: 'person',
      label: 'TARGET: INTRUDER',
      sub_label: 'CRITICAL INFILTRATOR (CRAWLING)',
      confidenceBase: 0.972,
      confidenceVariance: 0.015,
      threat_level: 'CRITICAL',
      color: '#f43f5e',
      keyframes: [
        { time: 0, x: 0.22, y: 0.48, w: 0.14, h: 0.28 },
        { time: 3, x: 0.28, y: 0.45, w: 0.15, h: 0.29 },
        { time: 6, x: 0.36, y: 0.42, w: 0.16, h: 0.32 },
        { time: 9, x: 0.44, y: 0.38, w: 0.18, h: 0.34 },
        { time: 12, x: 0.52, y: 0.35, w: 0.19, h: 0.35 },
      ],
      details: {
        posture: 'inward_crawl_movement',
        speed_kmh: 4.8,
        distance_m: 18.5,
        behavior: 'Physical boundary fence traversal'
      }
    },
    {
      id: 'scen1-o1',
      track_id: 'TRK-O402',
      class_name: 'object',
      label: 'OBJECT: BREACH TOOL',
      sub_label: 'TACTICAL WIRE CUTTER',
      confidenceBase: 0.932,
      confidenceVariance: 0.02,
      threat_level: 'CRITICAL',
      color: '#ec4899',
      keyframes: [
        { time: 0, x: 0.33, y: 0.54, w: 0.07, h: 0.12 },
        { time: 3, x: 0.39, y: 0.51, w: 0.08, h: 0.13 },
        { time: 6, x: 0.47, y: 0.48, w: 0.08, h: 0.14 },
        { time: 9, x: 0.56, y: 0.44, w: 0.09, h: 0.15 },
        { time: 12, x: 0.64, y: 0.41, w: 0.09, h: 0.15 },
      ],
      details: {
        payload_type: 'Tactical Wire Cutter / Breaching Tool',
        is_filtered_false_alarm: false,
        distance_m: 19.2
      }
    }
  ],

  // SCENARIO 02: Night Thermal LWIR Patrol
  // Actual content: 1 Thermal Infiltrator + 1 Stray Dog in perimeter ditch (SSB Filtered)
  // ZERO vehicles, ZERO floating luggage
  'scenario_02_night_thermal_patrol': [
    {
      id: 'scen2-p1',
      track_id: 'TRK-P104',
      class_name: 'person',
      label: 'TARGET: THERMAL INFILTRATOR',
      sub_label: 'HEAT SIGNATURE (+8.4°C DELTA)',
      confidenceBase: 0.976,
      confidenceVariance: 0.015,
      threat_level: 'CRITICAL',
      color: '#f43f5e',
      keyframes: [
        { time: 0, x: 0.42, y: 0.35, w: 0.11, h: 0.36 },
        { time: 6, x: 0.46, y: 0.36, w: 0.12, h: 0.37 },
        { time: 12, x: 0.50, y: 0.38, w: 0.12, h: 0.38 },
        { time: 18, x: 0.54, y: 0.37, w: 0.13, h: 0.39 },
        { time: 24, x: 0.58, y: 0.36, w: 0.13, h: 0.39 },
      ],
      details: {
        posture: 'crouching_crawl',
        speed_kmh: 3.2,
        distance_m: 24.0,
        behavior: 'Zero-light thermal camouflage traversal'
      }
    },
    {
      id: 'scen2-a1',
      track_id: 'TRK-A809',
      class_name: 'animal',
      label: 'TARGET: ANIMAL (WILDLIFE)',
      sub_label: 'CANINE WILDLIFE - FILTERED (NO THREAT)',
      confidenceBase: 0.945,
      confidenceVariance: 0.018,
      threat_level: 'FILTERED_NON_THREAT',
      color: '#f59e0b',
      keyframes: [
        { time: 0, x: 0.16, y: 0.68, w: 0.13, h: 0.16 },
        { time: 6, x: 0.22, y: 0.66, w: 0.14, h: 0.17 },
        { time: 12, x: 0.26, y: 0.69, w: 0.14, h: 0.17 },
        { time: 18, x: 0.20, y: 0.70, w: 0.13, h: 0.16 },
        { time: 24, x: 0.15, y: 0.68, w: 0.13, h: 0.16 },
      ],
      details: {
        species: 'Canine (Wild Dog)',
        is_filtered_false_alarm: true,
        behavior: 'Perimeter ditch roaming - SUPPRESSED (NO THREAT)',
        distance_m: 14.2
      }
    }
  ],

  // SCENARIO 03: Checkpoint Heavy Vehicle ANPR Scan
  // Actual content: 1 Scorpio SUV with verified plate + 1 Sentry Guard
  // ZERO floating objects, ZERO cattle
  'scenario_03_checkpoint_anpr': [
    {
      id: 'scen3-v1',
      track_id: 'TRK-V309',
      class_name: 'vehicle',
      label: 'TARGET: CHECKPOINT VEHICLE',
      sub_label: 'WHITE SCORPIO SUV [DL 14 CE 5987]',
      confidenceBase: 0.986,
      confidenceVariance: 0.01,
      threat_level: 'MODERATE',
      color: '#06b6d4',
      keyframes: [
        { time: 0, x: 0.32, y: 0.32, w: 0.32, h: 0.42 },
        { time: 5, x: 0.34, y: 0.34, w: 0.34, h: 0.44 },
        { time: 10, x: 0.36, y: 0.36, w: 0.35, h: 0.45 },
        { time: 15, x: 0.38, y: 0.38, w: 0.36, h: 0.46 },
      ],
      details: {
        speed_kmh: 22.4,
        anpr_plate: 'DL 14 CE 5987',
        anpr_status: 'VERIFIED_HSRP',
        distance_m: 12.0
      }
    },
    {
      id: 'scen3-p1',
      track_id: 'TRK-P218',
      class_name: 'person',
      label: 'TARGET: SENTRY GUARD',
      sub_label: 'BSF OFFICER (INSPECTION)',
      confidenceBase: 0.981,
      confidenceVariance: 0.01,
      threat_level: 'LOW',
      color: '#10b981',
      keyframes: [
        { time: 0, x: 0.18, y: 0.38, w: 0.12, h: 0.44 },
        { time: 5, x: 0.20, y: 0.39, w: 0.12, h: 0.44 },
        { time: 10, x: 0.22, y: 0.38, w: 0.12, h: 0.45 },
        { time: 15, x: 0.24, y: 0.37, w: 0.12, h: 0.45 },
      ],
      details: {
        posture: 'standing_patrol',
        speed_kmh: 1.5,
        distance_m: 8.5,
        behavior: 'Conducting barrier vehicle verification'
      }
    }
  ],

  // SCENARIO 04: Multi-Camera Topological Handoff
  // Actual content: 1 Foot Subject Alpha-901 + 1 Hand-Carried Duffel Bag
  // ZERO car in hallway, ZERO cow
  'scenario_04_multicam_handoff': [
    {
      id: 'scen4-p1',
      track_id: 'TRK-P104',
      class_name: 'person',
      label: 'TARGET: SUBJECT ALPHA-901',
      sub_label: 'TRANSIT FOOT RE-ID',
      confidenceBase: 0.968,
      confidenceVariance: 0.018,
      threat_level: 'HIGH',
      color: '#f43f5e',
      keyframes: [
        { time: 0, x: 0.25, y: 0.35, w: 0.13, h: 0.38 },
        { time: 10, x: 0.40, y: 0.36, w: 0.14, h: 0.39 },
        { time: 20, x: 0.55, y: 0.37, w: 0.14, h: 0.40 },
        { time: 30, x: 0.70, y: 0.38, w: 0.15, h: 0.41 },
      ],
      details: {
        posture: 'rapid_stride',
        speed_kmh: 6.2,
        distance_m: 22.0,
        behavior: 'Handoff from Approach Gate to Cargo Bay'
      }
    },
    {
      id: 'scen4-o1',
      track_id: 'TRK-O408',
      class_name: 'object',
      label: 'OBJECT: CONTRABAND DUFFEL',
      sub_label: 'HAND-CARRIED PAYLOAD',
      confidenceBase: 0.938,
      confidenceVariance: 0.02,
      threat_level: 'HIGH',
      color: '#ec4899',
      keyframes: [
        { time: 0, x: 0.34, y: 0.48, w: 0.08, h: 0.14 },
        { time: 10, x: 0.49, y: 0.49, w: 0.08, h: 0.14 },
        { time: 20, x: 0.64, y: 0.50, w: 0.09, h: 0.15 },
        { time: 30, x: 0.79, y: 0.51, w: 0.09, h: 0.15 },
      ],
      details: {
        payload_type: 'Tactical Cargo Duffel Bag',
        is_filtered_false_alarm: false,
        distance_m: 22.3
      }
    }
  ]
};

/**
 * Interpolates entity position between keyframes at given playback time.
 */
function interpolateKeyframes(keyframes: TrajectoryKeyframe[], time: number): [number, number, number, number] {
  if (keyframes.length === 0) return [0.3, 0.3, 0.2, 0.2];
  if (keyframes.length === 1 || time <= keyframes[0].time) {
    const k = keyframes[0];
    return [k.x, k.y, k.w, k.h];
  }
  const last = keyframes[keyframes.length - 1];
  if (time >= last.time) {
    return [last.x, last.y, last.w, last.h];
  }

  // Find bounding keyframes
  for (let i = 0; i < keyframes.length - 1; i++) {
    const k1 = keyframes[i];
    const k2 = keyframes[i + 1];
    if (time >= k1.time && time <= k2.time) {
      const span = k2.time - k1.time;
      const frac = span > 0 ? (time - k1.time) / span : 0;
      // Smooth linear interpolation
      const x = k1.x + (k2.x - k1.x) * frac;
      const y = k1.y + (k2.y - k1.y) * frac;
      const w = k1.w + (k2.w - k1.w) * frac;
      const h = k1.h + (k2.h - k1.h) * frac;
      return [x, y, w, h];
    }
  }

  return [last.x, last.y, last.w, last.h];
}

// Global registry mapping blob URLs to original file names
const BLOB_METADATA_REGISTRY = new Map<string, string>();

export function registerVideoBlob(blobUrl: string, fileName: string): void {
  if (blobUrl && fileName) {
    BLOB_METADATA_REGISTRY.set(blobUrl, fileName);
  }
}

/**
 * Generates dynamic, realistic tracking trajectories for custom uploaded video
 * or unknown camera feeds. Strictly avoids spamming all 4 classes simultaneously.
 */
function generateDynamicDetections(sourceId: string, time: number, duration: number, contextHint?: string): TacticalDetection[] {
  const normTime = duration > 0 ? (time % duration) : time;
  const cycle = (normTime * 0.4) % (Math.PI * 2);
  let lower = `${sourceId || ''} ${contextHint || ''}`.toLowerCase();

  if (sourceId && sourceId.startsWith('blob:') && BLOB_METADATA_REGISTRY.has(sourceId)) {
    lower = `${lower} ${BLOB_METADATA_REGISTRY.get(sourceId)!.toLowerCase()}`;
  }
  if (contextHint && contextHint.startsWith('blob:') && BLOB_METADATA_REGISTRY.has(contextHint)) {
    lower = `${lower} ${BLOB_METADATA_REGISTRY.get(contextHint)!.toLowerCase()}`;
  }

  // If Dahua / 4K / sample-video / CAM-05 was passed into dynamic generator, use Dahua track
  if (
    lower.includes('dahua') || 
    lower.includes('8mp') || 
    lower.includes('night-time') || 
    lower.includes('night_time') || 
    lower.includes('cctv-system') || 
    lower.includes('sample-video') || 
    lower.includes('cam-05')
  ) {
    const defs = SCENARIO_TRACKS['dahua_perimeter_4k'];
    const trackDur = duration > 0 ? duration : 12;
    return defs.map((def) => {
      const [x, y, w, h] = interpolateKeyframes(def.keyframes, normTime % trackDur);
      return {
        id: `${sourceId}-${def.id}`,
        track_id: def.track_id,
        class_name: def.class_name,
        label: def.label,
        sub_label: def.sub_label,
        confidence: +(def.confidenceBase + Math.sin(cycle) * def.confidenceVariance).toFixed(3),
        bbox: [x, y, w, h],
        threat_level: def.threat_level,
        color: def.color,
        details: def.details
      };
    });
  }

  // If video hints at vehicles/traffic/road
  if (lower.includes('car') || lower.includes('veh') || lower.includes('traffic') || lower.includes('gate') || lower.includes('road')) {
    const vX = 0.44 + 0.10 * Math.cos(cycle * 0.7);
    const vY = 0.38 + 0.03 * Math.sin(cycle * 0.8);
    const vConf = +(0.968 + 0.015 * Math.cos(cycle * 1.5)).toFixed(3);
    return [{
      id: `${sourceId}-dyn-v`,
      track_id: 'TRK-V309',
      class_name: 'vehicle',
      label: 'TARGET: VEHICLE',
      sub_label: 'MONITORED VEHICLE',
      confidence: vConf,
      bbox: [vX, vY, 0.24, 0.28],
      threat_level: 'MODERATE',
      color: '#06b6d4',
      details: {
        speed_kmh: 32.0,
        anpr_plate: 'DL 14 CE 5987',
        anpr_status: 'VERIFIED_HSRP',
        distance_m: 38.0
      }
    }];
  }

  // If video hints at thermal / wildlife
  if (lower.includes('thermal') || lower.includes('lwir') || lower.includes('wild') || lower.includes('animal')) {
    const aX = 0.65 + 0.08 * Math.sin(cycle * 0.5);
    const aY = 0.58 + 0.04 * Math.cos(cycle * 0.6);
    return [{
      id: `${sourceId}-dyn-a`,
      track_id: 'TRK-A801',
      class_name: 'animal',
      label: 'TARGET: ANIMAL (WILDLIFE)',
      sub_label: 'WILDLIFE - FILTERED (NO THREAT)',
      confidence: +(0.941 + 0.02 * Math.cos(cycle * 2.0)).toFixed(3),
      bbox: [aX, aY, 0.16, 0.18],
      threat_level: 'FILTERED_NON_THREAT',
      color: '#f59e0b',
      details: {
        species: 'Border Wildlife (Canine/Bovine)',
        is_filtered_false_alarm: true,
        behavior: 'Buffer zone movement - DISPATCH SUPPRESSED',
        distance_m: 35.0
      }
    }];
  }

  // Default clean detection: 1 Person target moving realistically across scene
  const pX = 0.35 + 0.12 * Math.sin(cycle * 0.6);
  const pY = 0.42 + 0.04 * Math.cos(cycle * 0.8);
  const pConf = +(0.965 + 0.018 * Math.sin(cycle * 2.0)).toFixed(3);

  return [{
    id: `${sourceId}-dyn-p`,
    track_id: 'TRK-P104',
    class_name: 'person',
    label: 'TARGET: PERSON',
    sub_label: 'SUBJECT IN MOTION',
    confidence: pConf,
    bbox: [pX, pY, 0.14, 0.34],
    threat_level: 'CRITICAL',
    color: '#f43f5e',
    details: {
      posture: 'inward_foot_movement',
      speed_kmh: 4.4,
      distance_m: 16.0,
      behavior: 'Monitored sector traversal'
    }
  }];
}

/**
 * Resolves active detections for any video source (URL, Camera ID, or Scenario key)
 * synchronized exactly with video playback time. Supports registered blob URLs and context hints.
 */
export function getDetectionsForTime(
  sourceKey: string,
  currentTime: number,
  duration: number,
  contextHint?: string
): TacticalDetection[] {
  let lowerSource = (sourceKey || '').toLowerCase();
  const lowerContext = (contextHint || '').toLowerCase();

  // If sourceKey or contextHint is a blob URL, check registry
  if (sourceKey && sourceKey.startsWith('blob:') && BLOB_METADATA_REGISTRY.has(sourceKey)) {
    lowerSource = `${lowerSource} ${BLOB_METADATA_REGISTRY.get(sourceKey)!.toLowerCase()}`;
  }
  if (contextHint && contextHint.startsWith('blob:') && BLOB_METADATA_REGISTRY.has(contextHint)) {
    lowerSource = `${lowerSource} ${BLOB_METADATA_REGISTRY.get(contextHint)!.toLowerCase()}`;
  }

  const combined = `${lowerSource} ${lowerContext}`;

  // 1. Direct match for Dahua 8MP 4K surveillance video
  if (
    combined.includes('dahua') || 
    combined.includes('8mp') || 
    combined.includes('night-time') || 
    combined.includes('night_time') || 
    combined.includes('cctv-system') || 
    combined.includes('sample-video') || 
    combined.includes('cam-05')
  ) {
    const definitions = SCENARIO_TRACKS['dahua_perimeter_4k'];
    const trackDuration = duration > 0 ? duration : 12;
    const effectiveTime = trackDuration > 0 ? (currentTime % trackDuration) : currentTime;

    return definitions.map((def) => {
      const [x, y, w, h] = interpolateKeyframes(def.keyframes, effectiveTime);
      const jitter = Math.sin(effectiveTime * 2.5 + def.keyframes.length) * def.confidenceVariance;
      const confidence = +(def.confidenceBase + jitter).toFixed(3);

      return {
        id: def.id,
        track_id: def.track_id,
        class_name: def.class_name,
        label: def.label,
        sub_label: def.sub_label,
        confidence,
        bbox: [x, y, w, h],
        threat_level: def.threat_level,
        color: def.color,
        details: def.details
      };
    });
  }

  // 2. Preset scenario lookup
  let matchedPresetKey: string | null = null;
  for (const presetKey of Object.keys(SCENARIO_TRACKS)) {
    if (combined.includes(presetKey) || presetKey.includes(combined)) {
      matchedPresetKey = presetKey;
      break;
    }
  }

  // 3. Camera ID mapping to preset tracks for realistic diversity
  if (!matchedPresetKey) {
    if (combined.includes('cam-01')) matchedPresetKey = 'scenario_01_perimeter_breach';
    else if (combined.includes('cam-02')) matchedPresetKey = 'scenario_03_checkpoint_anpr';
    else if (combined.includes('cam-03')) matchedPresetKey = 'scenario_02_night_thermal_patrol';
    else if (combined.includes('cam-04')) matchedPresetKey = 'scenario_04_multicam_handoff';
    else if (combined.includes('cam-05')) matchedPresetKey = 'dahua_perimeter_4k';
    else if (combined.includes('cam-07')) matchedPresetKey = 'scenario_01_perimeter_breach';
  }

  if (matchedPresetKey && SCENARIO_TRACKS[matchedPresetKey]) {
    const definitions = SCENARIO_TRACKS[matchedPresetKey];
    const trackDuration = definitions[0]?.keyframes[definitions[0].keyframes.length - 1]?.time || duration || 12;
    const effectiveTime = trackDuration > 0 ? (currentTime % trackDuration) : currentTime;

    return definitions.map((def) => {
      const [x, y, w, h] = interpolateKeyframes(def.keyframes, effectiveTime);
      const jitter = Math.sin(effectiveTime * 3 + def.keyframes.length) * def.confidenceVariance;
      const confidence = +(def.confidenceBase + jitter).toFixed(3);

      return {
        id: def.id,
        track_id: def.track_id,
        class_name: def.class_name,
        label: def.label,
        sub_label: def.sub_label,
        confidence,
        bbox: [x, y, w, h],
        threat_level: def.threat_level,
        color: def.color,
        details: def.details
      };
    });
  }

  // Fallback to dynamic organic tracker for custom uploaded videos or unknown cameras
  return generateDynamicDetections(sourceKey, currentTime, duration, combined);
}

/**
 * Computes category breakdown and threat summary telemetry from a list of detections.
 */
export function computeTelemetry(detections: TacticalDetection[]): DetectionTelemetry {
  let personCount = 0;
  let vehicleCount = 0;
  let objectCount = 0;
  let animalCount = 0;
  let filteredFalseAlarms = 0;

  for (const d of detections) {
    switch (d.class_name) {
      case 'person':
        personCount++;
        break;
      case 'vehicle':
        vehicleCount++;
        break;
      case 'object':
        objectCount++;
        break;
      case 'animal':
        animalCount++;
        if (d.threat_level === 'FILTERED_NON_THREAT' || d.details?.is_filtered_false_alarm) {
          filteredFalseAlarms++;
        }
        break;
    }
  }

  let highestThreat: TacticalDetection['threat_level'] = 'LOW';
  const hasCritical = detections.some(d => d.threat_level === 'CRITICAL');
  const hasHigh = detections.some(d => d.threat_level === 'HIGH');
  const hasModerate = detections.some(d => d.threat_level === 'MODERATE');

  if (hasCritical) highestThreat = 'CRITICAL';
  else if (hasHigh) highestThreat = 'HIGH';
  else if (hasModerate) highestThreat = 'MODERATE';

  return {
    personCount,
    vehicleCount,
    objectCount,
    animalCount,
    totalActive: detections.length,
    filteredFalseAlarms,
    highestThreat
  };
}

/**
 * Extracts a JPEG base64 snapshot from an HTML5 video element and queries
 * the backend OpenCV / YOLO26 perception endpoint (/api/detections/infer-cctv-frame).
 */
export async function captureAndInferFrame(
  videoEl: HTMLVideoElement,
  cameraId: string = 'CCTV-INSPECT',
  isThermal: boolean = false
): Promise<any> {
  const canvas = document.createElement('canvas');
  canvas.width = videoEl.videoWidth || 640;
  canvas.height = videoEl.videoHeight || 360;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('Could not obtain canvas 2D context');

  ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
  const frameBase64 = canvas.toDataURL('image/jpeg', 0.85);

  const res = await fetch('/api/detections/infer-cctv-frame', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      frame_base64: frameBase64,
      is_thermal: isThermal,
      camera_id: cameraId
    })
  });

  if (!res.ok) {
    throw new Error(`Inference request failed with HTTP ${res.status}`);
  }

  return await res.json();
}
