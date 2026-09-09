import React, { useState, useEffect } from 'react';
import { TacticalDetection, DetectionClass, DetectionTelemetry } from '../../types';
import { computeTelemetry } from '../../utils/detectionEngine';
import { 
  User, Car, Crosshair, Sparkles, 
  ShieldAlert, ShieldCheck, Filter, 
  CheckSquare, Square,
  PenTool, Check, Trash2, AlertTriangle
} from 'lucide-react';

/**
 * Standard Ray-Casting Algorithm for Point-in-Polygon Evaluation
 * Tests whether anchorPoint [x, y] in normalized (0..1) coordinates
 * resides inside the virtual fence polygon [[x1, y1], [x2, y2], ...].
 */
export function isPointInPolygon(point: [number, number], polygon: [number, number][]): boolean {
  if (!polygon || polygon.length < 3) return false;
  const [x, y] = point;
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [xi, yi] = polygon[i];
    const [xj, yj] = polygon[j];
    const intersect = ((yi > y) !== (yj > y)) && (x < ((xj - xi) * (y - yi)) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

interface TacticalDetectionOverlayProps {
  detections: TacticalDetection[];
  cameraName?: string;
  fps?: number;
  coordinates?: string;
  showFilters?: boolean;
  selectedTargetId?: string | null;
  onSelectTarget?: (id: string | null) => void;
  activeClasses?: Record<DetectionClass, boolean>;
  onToggleClass?: (cls: DetectionClass) => void;
  // Virtual Fencing Props (Section 2)
  virtualFencePolygon?: [number, number][];
  onUpdatePolygon?: (coords: [number, number][]) => void;
  isDrawingFence?: boolean;
  onToggleDrawingFence?: (drawing: boolean) => void;
  onIntrusionBreach?: (target: TacticalDetection) => void;
}

export const TacticalDetectionOverlay: React.FC<TacticalDetectionOverlayProps> = ({
  detections,
  cameraName = 'BOP-CAM-01',
  fps = 25.0,
  coordinates,
  showFilters = true,
  selectedTargetId = null,
  onSelectTarget,
  activeClasses: externalActiveClasses,
  onToggleClass: externalOnToggleClass,
  virtualFencePolygon: externalPolygon,
  onUpdatePolygon: externalOnUpdatePolygon,
  isDrawingFence: externalIsDrawing,
  onToggleDrawingFence: externalOnToggleDrawing,
  onIntrusionBreach
}) => {
  // Internal fallback state if parent doesn't provide state
  const [internalClasses, setInternalClasses] = useState<Record<DetectionClass, boolean>>({
    person: true,
    vehicle: true,
    object: true,
    animal: true,
  });

  const [internalPolygon, setInternalPolygon] = useState<[number, number][]>([]);
  const [internalIsDrawing, setInternalIsDrawing] = useState<boolean>(false);

  const activeClasses = externalActiveClasses || internalClasses;
  const activePolygon = externalPolygon !== undefined ? externalPolygon : internalPolygon;
  const activeIsDrawing = externalIsDrawing !== undefined ? externalIsDrawing : internalIsDrawing;

  const toggleClass = (cls: DetectionClass) => {
    if (externalOnToggleClass) {
      externalOnToggleClass(cls);
    } else {
      setInternalClasses((prev) => ({ ...prev, [cls]: !prev[cls] }));
    }
  };

  const updatePolygon = (coords: [number, number][]) => {
    if (externalOnUpdatePolygon) {
      externalOnUpdatePolygon(coords);
    } else {
      setInternalPolygon(coords);
    }
  };

  const toggleDrawing = (drawing: boolean) => {
    if (externalOnToggleDrawing) {
      externalOnToggleDrawing(drawing);
    } else {
      setInternalIsDrawing(drawing);
    }
  };

  // Strict confidence floor >= 0.25 to display all active detections
  const CONFIDENCE_THRESHOLD = 0.25;

  // Filter visible detections by active class and confidence
  const visibleDetections = detections.filter(
    (d) => activeClasses[d.class_name] !== false && (d.confidence ?? 0) >= CONFIDENCE_THRESHOLD
  );

  // Synchronize telemetry counts strictly to visible frame detections
  const telemetry: DetectionTelemetry = computeTelemetry(visibleDetections);

  // Point-in-polygon evaluation against all active targets (Section 2)
  const breachedTargets = visibleDetections.filter((target) => {
    if (activePolygon.length < 3) return false;
    const [nx, ny, nw, nh] = target.bbox;
    const anchorPoint: [number, number] = [nx + nw / 2, ny + nh];
    return isPointInPolygon(anchorPoint, activePolygon);
  });
  const hasIntrusion = breachedTargets.length > 0;

  // Notify parent of intrusion breach for real event logging
  useEffect(() => {
    if (hasIntrusion && onIntrusionBreach && breachedTargets[0]) {
      onIntrusionBreach(breachedTargets[0]);
    }
  }, [hasIntrusion, breachedTargets.map(b => b.track_id).join(',')]);

  // Handle polygon drawing canvas clicks
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!activeIsDrawing) return;
    const rect = e.currentTarget.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return;

    const nx = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const ny = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
    const newPt: [number, number] = [Math.round(nx * 1000) / 1000, Math.round(ny * 1000) / 1000];

    // If clicking near first point with >= 3 vertices, complete the fence
    if (activePolygon.length >= 3) {
      const [startNx, startNy] = activePolygon[0];
      const dist = Math.hypot(nx - startNx, ny - startNy);
      if (dist < 0.05) {
        toggleDrawing(false);
        return;
      }
    }

    updatePolygon([...activePolygon, newPt]);
  };

  return (
    <div 
      onClick={handleOverlayClick}
      className={`absolute inset-0 p-3.5 flex flex-col justify-between select-none font-mono z-20 ${
        activeIsDrawing ? 'cursor-crosshair pointer-events-auto bg-black/10' : 'pointer-events-none'
      }`}
    >
      
      {/* Top Telemetry & Sentinel HUD Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 pointer-events-auto">
        
        {/* Stream Status & Camera Identifier */}
        <div className="flex items-center space-x-2 bg-black/80 px-2.5 py-1 rounded-xl backdrop-blur-md border border-emerald-500/30 text-[10px]">
          <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
          <span className="font-bold text-white tracking-wider">REVIEWING</span>
          <span className="text-emerald-400 font-bold">[{cameraName}]</span>
        </div>

        {/* Live Multi-Class Detection Counters */}
        <div className="flex items-center space-x-1.5 bg-black/80 px-2 py-1 rounded-xl backdrop-blur-md border border-slate-800 text-[10px]">
          {/* Person counter */}
          <button
            onClick={() => toggleClass('person')}
            className={`flex items-center space-x-1 px-2 py-0.5 rounded-lg transition-all ${
              !activeClasses.person
                ? 'text-slate-600 line-through'
                : telemetry.personCount > 0
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold shadow-[0_0_8px_rgba(244,63,94,0.3)]'
                : 'text-slate-500 opacity-50'
            }`}
            title="Toggle Person Tracking"
          >
            <User className="w-3 h-3" />
            <span>PERSON: {telemetry.personCount}</span>
          </button>

          {/* Vehicle counter */}
          <button
            onClick={() => toggleClass('vehicle')}
            className={`flex items-center space-x-1 px-2 py-0.5 rounded-lg transition-all ${
              !activeClasses.vehicle
                ? 'text-slate-600 line-through'
                : telemetry.vehicleCount > 0
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold shadow-[0_0_8px_rgba(6,182,212,0.3)]'
                : 'text-slate-500 opacity-50'
            }`}
            title="Toggle Vehicle Tracking"
          >
            <Car className="w-3 h-3" />
            <span>VEHICLE: {telemetry.vehicleCount}</span>
          </button>

          {/* Objects counter */}
          <button
            onClick={() => toggleClass('object')}
            className={`flex items-center space-x-1 px-2 py-0.5 rounded-lg transition-all ${
              !activeClasses.object
                ? 'text-slate-600 line-through'
                : telemetry.objectCount > 0
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold shadow-[0_0_8px_rgba(168,85,247,0.3)]'
                : 'text-slate-500 opacity-50'
            }`}
            title="Toggle Objects Tracking"
          >
            <Crosshair className="w-3 h-3" />
            <span>OBJECTS: {telemetry.objectCount}</span>
          </button>

          {/* Animal counter (Border False Alarm Filter) */}
          <button
            onClick={() => toggleClass('animal')}
            className={`flex items-center space-x-1 px-2 py-0.5 rounded-lg transition-all ${
              !activeClasses.animal
                ? 'text-slate-600 line-through'
                : telemetry.animalCount > 0
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold shadow-[0_0_8px_rgba(245,158,11,0.3)]'
                : 'text-slate-500 opacity-50'
            }`}
            title="Toggle Animal Tracking (False Alarm Rejection)"
          >
            <Sparkles className="w-3 h-3" />
            <span>
              ANIMALS: {telemetry.animalCount}
              {telemetry.filteredFalseAlarms > 0 && (
                <span className="text-[9px] text-amber-400 ml-1">(FILTERED)</span>
              )}
            </span>
          </button>
        </div>

        {/* Neural Telemetry Badge */}
        <div className="hidden sm:flex items-center space-x-2 bg-black/80 px-2.5 py-1 rounded-xl backdrop-blur-md border border-cyan-500/30 text-[10px] text-cyan-300">
          <span>YOLOv8-ByteTrack</span>
          <span>•</span>
          <span>{fps.toFixed(1)} FPS</span>
          <span>•</span>
          <span className="text-emerald-400">8.2ms</span>
        </div>
      </div>

      {/* Active Drawing Banner if In Drawing Mode */}
      {activeIsDrawing && (
        <div className="self-center my-2 pointer-events-auto bg-slate-900/90 border border-cyan-400 text-cyan-300 px-4 py-2 rounded-xl backdrop-blur-md text-xs font-mono shadow-tactical-glow flex items-center space-x-3 animate-fade-in">
          <PenTool className="w-4 h-4 text-cyan-400 animate-bounce" />
          <span>
            CLICK VIDEO TO ADD VERTICES ({activePolygon.length} PTS). CLICK START POINT TO COMPLETE.
          </span>
          {activePolygon.length >= 3 && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleDrawing(false);
              }}
              className="px-2.5 py-1 rounded-lg bg-emerald-500 text-slate-950 font-bold hover:bg-emerald-400 flex items-center space-x-1 text-[11px]"
            >
              <Check className="w-3.5 h-3.5" />
              <span>FINISH FENCE</span>
            </button>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              updatePolygon([]);
              toggleDrawing(false);
            }}
            className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700 text-[11px]"
          >
            CANCEL
          </button>
        </div>
      )}

      {/* VIRTUAL FENCE SVG LAYER (Interactive & Intrusion Highlights) */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none z-10">
        {/* Closed Polygon Mesh */}
        {activePolygon.length >= 3 && (
          <polygon
            points={activePolygon.map(([px, py]) => `${px * 100}%,${py * 100}%`).join(' ')}
            fill={hasIntrusion ? 'rgba(244, 63, 94, 0.25)' : 'rgba(6, 182, 212, 0.12)'}
            stroke={hasIntrusion ? '#f43f5e' : '#06b6d4'}
            strokeWidth={hasIntrusion ? '3' : '2'}
            strokeDasharray={hasIntrusion ? '8 4' : '4 2'}
            className={hasIntrusion ? 'animate-pulse' : ''}
          />
        )}

        {/* Polylines while actively drawing */}
        {activeIsDrawing && activePolygon.length >= 2 && (
          <polyline
            points={activePolygon.map(([px, py]) => `${px * 100}%,${py * 100}%`).join(' ')}
            fill="none"
            stroke="#38bdf8"
            strokeWidth="2.5"
            strokeDasharray="5 3"
          />
        )}

        {/* Vertices Dots */}
        {activePolygon.map(([px, py], idx) => (
          <g key={idx}>
            <circle
              cx={`${px * 100}%`}
              cy={`${py * 100}%`}
              r={idx === 0 && activeIsDrawing ? '6' : '4.5'}
              fill={idx === 0 && activeIsDrawing ? '#10b981' : (hasIntrusion ? '#f43f5e' : '#38bdf8')}
              stroke="#ffffff"
              strokeWidth="1.5"
            />
            {activeIsDrawing && (
              <text
                x={`${px * 100 + 1}%`}
                y={`${py * 100 - 1}%`}
                fill="#ffffff"
                fontSize="10"
                fontFamily="monospace"
                fontWeight="bold"
              >
                P{idx + 1}
              </text>
            )}
          </g>
        ))}
      </svg>

      {/* Central Ambient Reticle */}
      {!activeIsDrawing && (
        <div className="self-center my-auto relative w-20 h-20 flex items-center justify-center pointer-events-none opacity-20">
          <div className="w-14 h-14 rounded-full border border-emerald-400/60 border-dashed animate-spin-slow" />
          <div className="absolute w-1.5 h-1.5 bg-emerald-400 rounded-full" />
        </div>
      )}

      {/* DYNAMIC REAL-TIME BOUNDING BOX OVERLAY */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {visibleDetections.map((target, idx) => {
          const [nx, ny, nw, nh] = target.bbox;
          const leftPct = `${(nx * 100).toFixed(2)}%`;
          const topPct = `${(ny * 100).toFixed(2)}%`;
          const widthPct = `${(nw * 100).toFixed(2)}%`;
          const heightPct = `${(nh * 100).toFixed(2)}%`;
          const isSelected = selectedTargetId === target.id;

          const isPerson = target.class_name === 'person';
          const isVehicle = target.class_name === 'vehicle';
          const isObject = target.class_name === 'object';
          const isAnimal = target.class_name === 'animal';

          // Point-in-polygon check for this individual target
          const anchorPoint: [number, number] = [nx + nw / 2, ny + nh];
          const isTargetInBreach = activePolygon.length >= 3 && isPointInPolygon(anchorPoint, activePolygon);

          // Detect potential label collision
          const hasCollision = visibleDetections.slice(0, idx).some((prev) => {
            const [px, py] = prev.bbox;
            return Math.abs(px - nx) < 0.16 && Math.abs(py - ny) < 0.08;
          });

          let labelPositionClass = "-top-6 left-0";
          if (ny < 0.07) {
            labelPositionClass = "top-1 left-1";
          } else if (hasCollision) {
            labelPositionClass = "top-[calc(100%+3px)] left-0";
          }

          let borderTheme = 'border-rose-500 shadow-[0_0_12px_rgba(244,63,94,0.3)]';
          let bgTheme = 'bg-rose-500/10';
          let headerBadgeBg = 'bg-rose-600 text-white';

          if (isTargetInBreach) {
            borderTheme = 'border-rose-500 ring-2 ring-rose-500 shadow-[0_0_20px_rgba(244,63,94,0.6)] animate-pulse';
            bgTheme = 'bg-rose-500/25';
            headerBadgeBg = 'bg-rose-600 text-white font-black';
          } else if (isVehicle) {
            borderTheme = 'border-cyan-400 shadow-[0_0_12px_rgba(6,182,212,0.3)]';
            bgTheme = 'bg-cyan-500/10';
            headerBadgeBg = 'bg-cyan-500 text-slate-950 font-bold';
          } else if (isObject) {
            borderTheme = 'border-purple-500 shadow-[0_0_12px_rgba(168,85,247,0.3)]';
            bgTheme = 'bg-purple-500/10';
            headerBadgeBg = 'bg-purple-600 text-white';
          } else if (isAnimal) {
            borderTheme = 'border-amber-400 shadow-[0_0_12px_rgba(245,158,11,0.3)]';
            bgTheme = 'bg-amber-500/10';
            headerBadgeBg = 'bg-amber-500 text-slate-950 font-bold';
          }

          const hasPlate = isVehicle && (target.details?.anpr_plate || target.details?.plate_bbox);
          const plateText = target.details?.anpr_plate;
          const ocrConfidence = target.details?.confidence_percentage_ocr || `${Math.round((target.confidence || 0.9) * 100)}%`;
          const isVerified = !target.details?.requires_human_verification;

          return (
            <div
              key={target.id}
              onClick={(e) => {
                e.stopPropagation();
                onSelectTarget && onSelectTarget(isSelected ? null : target.id);
              }}
              style={{
                left: leftPct,
                top: topPct,
                width: widthPct,
                height: heightPct,
              }}
              className={`absolute transition-all duration-100 pointer-events-auto cursor-pointer rounded-sm ${borderTheme} ${bgTheme} ${
                isSelected ? 'ring-2 ring-white scale-[1.02] z-30' : 'z-10'
              }`}
            >
              {/* Corner Brackets */}
              <div className="absolute -top-1 -left-1 w-2.5 h-2.5 border-t-2 border-l-2 border-white pointer-events-none" />
              <div className="absolute -top-1 -right-1 w-2.5 h-2.5 border-t-2 border-r-2 border-white pointer-events-none" />
              <div className="absolute -bottom-1 -left-1 w-2.5 h-2.5 border-b-2 border-l-2 border-white pointer-events-none" />
              <div className="absolute -bottom-1 -right-1 w-2.5 h-2.5 border-b-2 border-r-2 border-white pointer-events-none" />

              {/* Target Identification Header */}
              <div className={`absolute ${labelPositionClass} flex items-center space-x-1 whitespace-nowrap pointer-events-none z-20`}>
                <div className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold flex items-center space-x-1 shadow-lg border border-white/20 ${headerBadgeBg}`}>
                  {isPerson && <User className="w-2.5 h-2.5" />}
                  {isVehicle && <Car className="w-2.5 h-2.5" />}
                  {isObject && <Crosshair className="w-2.5 h-2.5" />}
                  {isAnimal && <Sparkles className="w-2.5 h-2.5" />}
                  <span>{target.track_id}</span>
                  <span>({Math.round((target.confidence ?? 0.85) * 100)}%)</span>
                  {isTargetInBreach && (
                    <span className="bg-white text-rose-700 px-1 rounded text-[8px] font-black animate-pulse">
                      BREACH
                    </span>
                  )}
                </div>

                {!isTargetInBreach && (
                  <div className="px-1 py-0.5 rounded text-[8px] font-mono bg-black/80 backdrop-blur-md border border-slate-700 text-slate-300">
                    {isAnimal && (
                      <span className="text-amber-400 font-bold flex items-center space-x-0.5">
                        <ShieldCheck className="w-2.5 h-2.5 text-emerald-400" />
                        <span>FILTERED</span>
                      </span>
                    )}
                    {isPerson && (
                      <span className="text-rose-300 font-bold flex items-center space-x-0.5">
                        <ShieldAlert className="w-2.5 h-2.5 text-rose-400" />
                        <span>{target.details?.behavior || target.sub_label || 'ACTIVE'}</span>
                      </span>
                    )}
                    {isVehicle && (
                      <span className="text-cyan-300 font-bold">
                        {target.details?.anpr_plate ? `[${target.details.anpr_plate}]` : (target.sub_label || 'MONITORED')}
                      </span>
                    )}
                    {isObject && (
                      <span className="text-purple-300 font-bold">
                        {target.details?.payload_type || target.sub_label || 'PAYLOAD'}
                      </span>
                    )}
                  </div>
                )}
              </div>

              {/* ANPR Vehicle Optical License Plate Overlay Bracket (Section 3) */}
              {hasPlate && plateText && (
                <div className="absolute bottom-1 left-1 right-1 bg-black/90 border border-amber-400 rounded px-1.5 py-0.5 shadow-lg flex items-center justify-between text-[9px] font-mono z-20 pointer-events-none">
                  <div className="flex items-center space-x-1 min-w-0">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping" />
                    <span className="font-black text-amber-300 tracking-wider truncate">
                      {plateText}
                    </span>
                  </div>
                  <div className="flex items-center space-x-1 flex-shrink-0 ml-1">
                    <span className="text-[8px] text-slate-300">{ocrConfidence}</span>
                    <span className={`text-[8px] px-1 rounded font-bold ${
                      isVerified
                        ? 'bg-emerald-500/30 text-emerald-300 border border-emerald-500/50'
                        : 'bg-amber-500/30 text-amber-300 border border-amber-500/50'
                    }`}>
                      {isVerified ? 'VERIFIED' : 'UNVERIFIED'}
                    </span>
                  </div>
                </div>
              )}

              {/* Center Lock-on Reticle if Selected */}
              {isSelected && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="w-8 h-8 rounded-full border border-white/80 animate-ping" />
                  <Crosshair className="w-5 h-5 text-white" />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Bottom Metadata & Tactical Virtual Fence Controls Ribbon */}
      <div className="flex flex-wrap items-center justify-between gap-2 pointer-events-auto">
        {coordinates && (
          <div className="bg-black/80 px-2.5 py-1 rounded-xl backdrop-blur-md border border-emerald-500/20 text-[10px] text-emerald-400">
            <span>COORDS: {coordinates}</span>
          </div>
        )}

        {/* Virtual Fence Interactive Controls (Section 2) */}
        <div className="flex items-center space-x-1.5 bg-black/80 px-2.5 py-1 rounded-xl backdrop-blur-md border border-slate-800 text-[10px]">
          <span className="text-slate-400 flex items-center space-x-1 mr-1">
            <PenTool className="w-3 h-3 text-cyan-400" />
            <span>FENCE:</span>
          </span>

          <button
            onClick={() => toggleDrawing(!activeIsDrawing)}
            className={`px-2 py-0.5 rounded text-[9px] font-bold flex items-center space-x-1 transition-all ${
              activeIsDrawing
                ? 'bg-cyan-500 text-slate-950 font-black shadow-tactical-glow animate-pulse'
                : 'bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-500/40'
            }`}
            title="Click on video feed to draw custom perimeter polygon"
          >
            <PenTool className="w-2.5 h-2.5" />
            <span>{activeIsDrawing ? 'DRAWING...' : (activePolygon.length >= 3 ? 'EDIT FENCE' : 'DRAW FENCE')}</span>
          </button>

          {activeIsDrawing && activePolygon.length >= 3 && (
            <button
              onClick={() => toggleDrawing(false)}
              className="px-2 py-0.5 rounded text-[9px] font-bold bg-emerald-500 text-slate-950 hover:bg-emerald-400 flex items-center space-x-1"
            >
              <Check className="w-2.5 h-2.5" />
              <span>CLOSE</span>
            </button>
          )}

          {activePolygon.length > 0 && (
            <button
              onClick={() => {
                updatePolygon([]);
                toggleDrawing(false);
              }}
              className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-rose-500/20 text-rose-300 hover:bg-rose-500/30 border border-rose-500/40 flex items-center space-x-1"
              title="Clear Polygon"
            >
              <Trash2 className="w-2.5 h-2.5" />
              <span>CLEAR</span>
            </button>
          )}

          {activePolygon.length === 0 && (
            <button
              onClick={() => {
                updatePolygon([[0.15, 0.45], [0.85, 0.45], [0.90, 0.90], [0.10, 0.90]]);
              }}
              className="px-2 py-0.5 rounded text-[9px] font-bold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 flex items-center space-x-1"
              title="Load Standard Border Restricted Zone"
            >
              <span>DEFAULT ZONE</span>
            </button>
          )}

          {hasIntrusion && (
            <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-rose-600 text-white flex items-center space-x-1 animate-pulse border border-rose-400">
              <AlertTriangle className="w-2.5 h-2.5" />
              <span>BREACH ({breachedTargets.length})</span>
            </span>
          )}
        </div>

        {/* Interactive Filter Controls */}
        {showFilters && (
          <div className="flex items-center space-x-1.5 bg-black/80 px-2.5 py-1 rounded-xl backdrop-blur-md border border-slate-800 text-[10px]">
            <span className="text-slate-400 flex items-center space-x-1 mr-1">
              <Filter className="w-3 h-3" />
              <span>HUD:</span>
            </span>

            <button
              onClick={() => toggleClass('person')}
              className={`px-1.5 py-0.5 rounded text-[9px] font-bold flex items-center space-x-1 transition-colors ${
                activeClasses.person ? 'bg-rose-500/20 text-rose-300 border border-rose-500/50' : 'text-slate-500'
              }`}
            >
              {activeClasses.person ? <CheckSquare className="w-2.5 h-2.5" /> : <Square className="w-2.5 h-2.5" />}
              <span>Person</span>
            </button>

            <button
              onClick={() => toggleClass('vehicle')}
              className={`px-1.5 py-0.5 rounded text-[9px] font-bold flex items-center space-x-1 transition-colors ${
                activeClasses.vehicle ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50' : 'text-slate-500'
              }`}
            >
              {activeClasses.vehicle ? <CheckSquare className="w-2.5 h-2.5" /> : <Square className="w-2.5 h-2.5" />}
              <span>Vehicle</span>
            </button>

            <button
              onClick={() => toggleClass('object')}
              className={`px-1.5 py-0.5 rounded text-[9px] font-bold flex items-center space-x-1 transition-colors ${
                activeClasses.object ? 'bg-purple-500/20 text-purple-300 border border-purple-500/50' : 'text-slate-500'
              }`}
            >
              {activeClasses.object ? <CheckSquare className="w-2.5 h-2.5" /> : <Square className="w-2.5 h-2.5" />}
              <span>Objects</span>
            </button>

            <button
              onClick={() => toggleClass('animal')}
              className={`px-1.5 py-0.5 rounded text-[9px] font-bold flex items-center space-x-1 transition-colors ${
                activeClasses.animal ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50' : 'text-slate-500'
              }`}
            >
              {activeClasses.animal ? <CheckSquare className="w-2.5 h-2.5" /> : <Square className="w-2.5 h-2.5" />}
              <span>Animals</span>
            </button>
          </div>
        )}

        <div className="bg-black/80 px-2.5 py-1 rounded-xl backdrop-blur-md border border-emerald-500/20 text-[10px] text-emerald-400">
          <span>ACTIVE TARGETS: {visibleDetections.length}</span>
        </div>
      </div>

    </div>
  );
};
