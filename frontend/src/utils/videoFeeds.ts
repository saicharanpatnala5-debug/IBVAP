/**
 * Tactical Video Feeds Resolver for IBVAP Multi-Spectral Sensors
 */

export const CAMERA_VIDEO_MAP: Record<string, string> = {
  'CAM-01': '/videos/scenario_01_perimeter_breach.mp4',
  'CAM-02': '/videos/scenario_03_checkpoint_anpr.mp4',
  'CAM-03': '/videos/scenario_02_night_thermal_patrol.mp4',
  'CAM-04': '/videos/scenario_04_multicam_handoff.mp4',
  'CAM-05': '/videos/night-time---8mp-4k-dahua-cctv-system-sample-video.mp4',
  'CAM-07': '/videos/scenario_01_perimeter_breach.mp4',
};

export const DEFAULT_CCTV_VIDEO = '/videos/scenario_01_perimeter_breach.mp4';

export function getCameraVideoUrl(cameraId?: string, fallbackUrl?: string): string {
  if (!cameraId) return fallbackUrl || DEFAULT_CCTV_VIDEO;
  return CAMERA_VIDEO_MAP[cameraId] || fallbackUrl || DEFAULT_CCTV_VIDEO;
}
