import { useState, useRef, useCallback, useEffect } from 'react';
import { TacticalDetection, DetectionTelemetry } from '../types';
import { computeTelemetry, registerVideoBlob } from '../utils/detectionEngine';

/**
 * Tactical Video Context Structure
 * Captures live stream metadata, playback status, telemetry, and pipeline health.
 */
export interface CurrentVideoContext {
  streamId: string | null;
  fileName: string | null;
  videoUrl: string | null;
  fps: number;
  resolution: string;
  duration: number;
  currentTime: number;
  status: 'IDLE' | 'LOADING' | 'PLAYING' | 'PAUSED' | 'TEARDOWN';
  activeModel: string;
  sourceType: 'LOCAL_UPLOAD' | 'RTSP_STREAM' | 'PRESET' | null;
  telemetry: DetectionTelemetry | null;
  createdAt: string;
}

export interface UseVideoPlayerStateReturn {
  // Video Context & Status
  currentVideoContext: CurrentVideoContext | null;
  videoUrl: string | null;
  videoTitle: string;
  isPlaying: boolean;
  isLooping: boolean;
  isMuted: boolean;
  currentTime: number;
  duration: number;
  playbackSpeed: number;

  // Tracking & Detections
  trackingArrays: TacticalDetection[];
  activeTracks: string[];
  telemetry: DetectionTelemetry;

  // DOM Refs
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
  videoRef: React.RefObject<HTMLVideoElement | null>;

  // Controls & Actions
  setIsPlaying: (playing: boolean) => void;
  setIsLooping: (looping: boolean) => void;
  setIsMuted: (muted: boolean) => void;
  setCurrentTime: (time: number) => void;
  setDuration: (duration: number) => void;
  setPlaybackSpeed: (speed: number) => void;
  setTrackingArrays: (detections: TacticalDetection[]) => void;

  // Strict Teardown & File Ingestion
  strictTeardown: () => void;
  handleFileUpload: (file: File) => void;
  loadStreamUrl: (url: string, title?: string, sourceType?: 'RTSP_STREAM' | 'PRESET') => void;
}

/**
 * useVideoPlayerState
 * High-performance state manager for tactical video feeds and CCTV ingestion.
 * Enforces strict memory flushes and canvas clearing on stream handoffs.
 */
export function useVideoPlayerState(
  initialUrl?: string,
  initialTitle?: string
): UseVideoPlayerStateReturn {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const [currentVideoContext, setCurrentVideoContext] = useState<CurrentVideoContext | null>(
    initialUrl
      ? {
          streamId: `stream-${Date.now()}`,
          fileName: initialTitle || 'Default Feed',
          videoUrl: initialUrl,
          fps: 25.0,
          resolution: '1920x1080',
          duration: 0,
          currentTime: 0,
          status: 'IDLE',
          activeModel: 'yolo26x',
          sourceType: 'PRESET',
          telemetry: null,
          createdAt: new Date().toISOString(),
        }
      : null
  );

  const [videoUrl, setVideoUrl] = useState<string | null>(initialUrl || null);
  const [videoTitle, setVideoTitle] = useState<string>(initialTitle || 'Tactical Feed');
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [isLooping, setIsLooping] = useState<boolean>(true);
  const [isMuted, setIsMuted] = useState<boolean>(true);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);

  // Tracking arrays
  const [trackingArrays, setTrackingArrays] = useState<TacticalDetection[]>([]);
  const [activeTracks, setActiveTracks] = useState<string[]>([]);

  const telemetry = computeTelemetry(trackingArrays);

  /**
   * STRICT TEARDOWN & MEMORY FLUSH
   * Mandated by IBVAP architecture before initializing any new video stream:
   * 1. Clears the previous video's canvas context completely.
   * 2. Resets all tracking arrays to [] and active tracks to [].
   * 3. Flushes currentVideoContext to null.
   * 4. Revokes previous blob URLs to prevent browser memory leaks.
   * 5. Unloads HTML5 video element buffers.
   */
  const strictTeardown = useCallback(() => {
    // 1. Explicitly clear previous video's canvas
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath();
      }
    }

    // 2. Reset all tracking arrays to empty
    setTrackingArrays([]);
    setActiveTracks([]);

    // 3. Flush the currentVideoContext
    setCurrentVideoContext(null);

    // 4. Revoke previous blob URL if exists
    if (videoUrl && videoUrl.startsWith('blob:')) {
      try {
        URL.revokeObjectURL(videoUrl);
      } catch (err) {
        console.warn('[VideoStateManager] Blob revoke warning:', err);
      }
    }

    // 5. Stop and detach video element
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.removeAttribute('src');
      videoRef.current.load();
    }

    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
  }, [videoUrl]);

  /**
   * Ingestion Handler for File Uploads
   * STRICTLY executes strictTeardown() before initializing the new video stream.
   */
  const handleFileUpload = useCallback(
    (file: File) => {
      // FORCED MEMORY FLUSH BEFORE INITIALIZING NEW STREAM
      strictTeardown();

      // Create new blob stream
      const objectUrl = URL.createObjectURL(file);
      registerVideoBlob(objectUrl, file.name);

      setVideoUrl(objectUrl);
      setVideoTitle(file.name);

      const newContext: CurrentVideoContext = {
        streamId: `stream-upload-${Date.now()}`,
        fileName: file.name,
        videoUrl: objectUrl,
        fps: 30.0,
        resolution: '1920x1080',
        duration: 0,
        currentTime: 0,
        status: 'LOADING',
        activeModel: 'yolo26x',
        sourceType: 'LOCAL_UPLOAD',
        telemetry: null,
        createdAt: new Date().toISOString(),
      };

      setCurrentVideoContext(newContext);

      // Auto-attach and start playback
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.currentTime = 0;
          videoRef.current.loop = isLooping;
          videoRef.current.muted = isMuted;
          videoRef.current
            .play()
            .then(() => {
              setIsPlaying(true);
              setCurrentVideoContext((prev) => (prev ? { ...prev, status: 'PLAYING' } : null));
            })
            .catch(() => {
              if (videoRef.current) {
                videoRef.current.muted = true;
                setIsMuted(true);
                videoRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
              }
            });
        }
      }, 80);
    },
    [strictTeardown, isLooping, isMuted]
  );

  /**
   * Ingestion Handler for RTSP / Stream URLs
   */
  const loadStreamUrl = useCallback(
    (url: string, title?: string, sourceType: 'RTSP_STREAM' | 'PRESET' = 'RTSP_STREAM') => {
      // FORCED MEMORY FLUSH BEFORE INITIALIZING NEW STREAM
      strictTeardown();

      setVideoUrl(url);
      setVideoTitle(title || 'Live Tactical RTSP Stream');

      const newContext: CurrentVideoContext = {
        streamId: `stream-rtsp-${Date.now()}`,
        fileName: title || 'Live RTSP Stream',
        videoUrl: url,
        fps: 25.0,
        resolution: '1920x1080',
        duration: 0,
        currentTime: 0,
        status: 'LOADING',
        activeModel: 'yolo26s',
        sourceType,
        telemetry: null,
        createdAt: new Date().toISOString(),
      };

      setCurrentVideoContext(newContext);

      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.currentTime = 0;
          videoRef.current.loop = isLooping;
          videoRef.current.muted = isMuted;
          videoRef.current
            .play()
            .then(() => {
              setIsPlaying(true);
              setCurrentVideoContext((prev) => (prev ? { ...prev, status: 'PLAYING' } : null));
            })
            .catch(() => {});
        }
      }, 80);
    },
    [strictTeardown, isLooping, isMuted]
  );

  // Auto clean-up on unmount
  useEffect(() => {
    return () => {
      if (videoUrl && videoUrl.startsWith('blob:')) {
        try {
          URL.revokeObjectURL(videoUrl);
        } catch {
          // ignore
        }
      }
    };
  }, [videoUrl]);

  return {
    currentVideoContext,
    videoUrl,
    videoTitle,
    isPlaying,
    isLooping,
    isMuted,
    currentTime,
    duration,
    playbackSpeed,
    trackingArrays,
    activeTracks,
    telemetry,
    canvasRef,
    videoRef,
    setIsPlaying,
    setIsLooping,
    setIsMuted,
    setCurrentTime,
    setDuration,
    setPlaybackSpeed,
    setTrackingArrays,
    strictTeardown,
    handleFileUpload,
    loadStreamUrl,
  };
}
