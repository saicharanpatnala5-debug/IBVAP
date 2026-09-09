import React, { useState } from 'react';

/**
 * ForensicPlayer component implementing the standard forensic video processing pipeline.
 * Submits uploaded/selected CCTV video to FastAPI POST /api/analyze_video,
 * receives the processed video URL with drawn YOLO bounding boxes, and plays it in HTML5 <video>.
 */
export const ForensicPlayer: React.FC<{
  videoSrc?: string;
  videoTitle?: string;
}> = ({ 
  videoSrc = '/videos/scenario_01_perimeter_breach.mp4',
  videoTitle = 'Perimeter Security Camera CAM-01' 
}) => {
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [processedUrl, setProcessedUrl] = useState<string | null>(null);
  const [detectedClasses, setDetectedClasses] = useState<string[]>([]);
  const [riskScore, setRiskScore] = useState<number | null>(null);
  const [isProcessedActive, setIsProcessedActive] = useState<boolean>(false);

  const handleStartForensicAnalysis = async () => {
    if (isProcessedActive) {
      setIsProcessedActive(false);
      return;
    }
    if (processedUrl) {
      setIsProcessedActive(true);
      return;
    }

    setIsProcessing(true);
    try {
      const resp = await fetch(videoSrc);
      const blob = await resp.blob();
      const filename = videoSrc.split('/').pop() || 'cctv_footage.mp4';
      const file = new File([blob], filename, { type: 'video/mp4' });

      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch('http://127.0.0.1:8000/api/analyze_video', {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        setProcessedUrl(data.processed_video_url);
        setDetectedClasses(data.detected_classes || []);
        setRiskScore(data.risk_score || 30);
        setIsProcessedActive(true);
      } else {
        console.warn('Analysis endpoint error, falling back to raw video');
      }
    } catch (e) {
      console.error('Forensic analysis failed:', e);
    } finally {
      setIsProcessing(false);
    }
  };

  const activeSrc = isProcessedActive && processedUrl ? processedUrl : videoSrc;

  return (
    <div className="relative aspect-video w-full rounded-2xl bg-black border border-slate-800 overflow-hidden shadow-2xl flex flex-col items-center justify-center group">
      {/* Video Viewport: Standard HTML5 Video Player playing either raw or processed inference video */}
      <div className="relative w-full h-full flex items-center justify-center bg-black overflow-hidden">
        <video
          key={activeSrc}
          src={activeSrc}
          autoPlay
          loop
          muted
          controls
          playsInline
          className="w-full h-full object-cover"
        />

        {/* Live HUD Badge */}
        <div className="absolute top-3 left-3 z-20 flex items-center space-x-2 bg-slate-900/90 backdrop-blur px-3 py-1.5 rounded-xl border border-emerald-500/50 shadow-tactical-glow">
          <span className={`w-2.5 h-2.5 rounded-full ${isProcessedActive ? 'bg-emerald-500 animate-pulse' : 'bg-slate-500'}`} />
          <span className="text-[11px] font-mono font-bold text-emerald-400 uppercase tracking-wider">
            {isProcessedActive ? 'YOLO FORENSIC PROCESSED' : 'RAW CCTV FOOTAGE'}
          </span>
          {riskScore !== null && isProcessedActive && (
            <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${riskScore >= 70 ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' : 'bg-emerald-500/20 text-emerald-300'}`}>
              RISK: {riskScore}/100
            </span>
          )}
        </div>

        {detectedClasses.length > 0 && isProcessedActive && (
          <div className="absolute top-3 right-3 z-20 flex items-center space-x-1.5 bg-slate-900/90 backdrop-blur px-3 py-1.5 rounded-xl border border-cyan-500/40">
            <span className="text-[10px] font-mono text-cyan-300 font-bold">
              TARGETS: {detectedClasses.join(', ').toUpperCase()}
            </span>
          </div>
        )}
      </div>

      {/* Forensic Control Ribbon */}
      <div className="absolute bottom-4 left-4 right-4 z-20 flex items-center justify-between pointer-events-auto bg-slate-900/90 backdrop-blur-md px-4 py-2.5 rounded-xl border border-slate-700 shadow-2xl font-mono text-xs">
        <span className="text-slate-300">
          Source: <strong className="text-white">{videoTitle}</strong>
        </span>

        <button
          onClick={handleStartForensicAnalysis}
          disabled={isProcessing}
          className={`px-4 py-2 rounded-lg font-bold text-xs transition-all shadow-tactical-glow flex items-center space-x-2 ${
            isProcessing
              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50 animate-pulse'
              : isProcessedActive
              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/50 hover:bg-rose-500/30'
              : 'bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-obsidian'
          }`}
        >
          <span>
            {isProcessing
              ? '⚡ Running YOLO Inference Pipeline...'
              : isProcessedActive
              ? 'Reset to Raw Video'
              : '⚡ Start AI Forensic Analysis'}
          </span>
        </button>
      </div>
    </div>
  );
};

export default ForensicPlayer;
