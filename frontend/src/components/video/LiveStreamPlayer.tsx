import React, { useRef, useEffect } from 'react';
import { HUDOverlay } from './HUDOverlay';
import { Camera } from '../../types';

interface LiveStreamPlayerProps {
  camera: Camera;
}

export const LiveStreamPlayer: React.FC<LiveStreamPlayerProps> = ({ camera }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let frameId: number;
    let scanLine = 0;

    const render = () => {
      ctx.fillStyle = '#080d18';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.strokeStyle = 'rgba(16, 185, 129, 0.08)';
      ctx.lineWidth = 1;
      for (let x = 0; x < canvas.width; x += 30) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
      }
      for (let y = 0; y < canvas.height; y += 30) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }

      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 2;
      ctx.strokeRect(180, 100, 90, 160);
      ctx.fillStyle = '#10b981';
      ctx.font = '10px monospace';
      ctx.fillText('PERSON: 94.2%', 180, 92);

      scanLine = (scanLine + 2) % canvas.height;
      ctx.strokeStyle = 'rgba(6, 182, 212, 0.3)';
      ctx.beginPath();
      ctx.moveTo(0, scanLine);
      ctx.lineTo(canvas.width, scanLine);
      ctx.stroke();

      frameId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(frameId);
  }, []);

  return (
    <div className="relative aspect-video rounded-3xl overflow-hidden bg-black border border-slate-800 shadow-2xl">
      <canvas
        ref={canvasRef}
        width={640}
        height={360}
        className="w-full h-full object-cover"
      />
      <HUDOverlay cameraName={camera.name} fps={camera.fps} />
    </div>
  );
};
