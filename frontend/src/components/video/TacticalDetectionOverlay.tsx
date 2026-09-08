import React, { useState } from 'react';
import { TacticalDetection, DetectionClass, DetectionTelemetry } from '../../types';
import { computeTelemetry } from '../../utils/detectionEngine';
import { 
  User, Car, Crosshair, Sparkles, 
  ShieldAlert, ShieldCheck, Filter, 
  Layers, CheckSquare, Square
} from 'lucide-react';

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
}

export const TacticalDetectionOverlay: React.FC<TacticalDetectionOverlayProps> = ({
  detections,
  cameraName = 'BOP-CAM-01',
  fps = 25.0,
  coordinates = '28.6139° N, 77.2090° E',
  showFilters = true,
  selectedTargetId = null,
  onSelectTarget,
  activeClasses: externalActiveClasses,
  onToggleClass: externalOnToggleClass,
}) => {
  // Internal state if parent doesn't provide state
  const [internalClasses, setInternalClasses] = useState<Record<DetectionClass, boolean>>({
    person: true,
    vehicle: true,
    object: true,
    animal: true,
  });

  const activeClasses = externalActiveClasses || internalClasses;
  const toggleClass = (cls: DetectionClass) => {
    if (externalOnToggleClass) {
      externalOnToggleClass(cls);
    } else {
      setInternalClasses((prev) => ({ ...prev, [cls]: !prev[cls] }));
    }
  };

  const telemetry: DetectionTelemetry = computeTelemetry(detections);

  // Filter visible detections
  const visibleDetections = detections.filter(
    (d) => activeClasses[d.class_name] !== false
  );

  return (
    <div className="absolute inset-0 pointer-events-none p-3.5 flex flex-col justify-between select-none font-mono z-20">
      
      {/* Top Telemetry & Sentinel HUD Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 pointer-events-auto">
        
        {/* Stream Status & Camera Identifier */}
        <div className="flex items-center space-x-2 bg-black/80 px-2.5 py-1 rounded-xl backdrop-blur-md border border-emerald-500/30 text-[10px]">
          <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
          <span className="font-bold text-white tracking-wider">LIVE SENTINEL</span>
          <span className="text-emerald-400 font-bold">[{cameraName}]</span>
        </div>

        {/* Live Multi-Class Detection Counters (PERSON, VEHICLE, OBJECT, ANIMAL) */}
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
            title="Toggle Objects & Weapons Tracking"
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
          <span>YOLO26s</span>
          <span>•</span>
          <span>{fps.toFixed(1)} FPS</span>
          <span>•</span>
          <span className="text-emerald-400">8.2ms</span>
        </div>
      </div>

      {/* Central Screen Crosshair Reticle (Subtle Tactical Ambience) */}
      <div className="self-center my-auto relative w-20 h-20 flex items-center justify-center pointer-events-none opacity-25">
        <div className="w-14 h-14 rounded-full border border-emerald-400/60 border-dashed animate-spin-slow" />
        <div className="absolute w-1.5 h-1.5 bg-emerald-400 rounded-full" />
        <div className="absolute top-0 w-0.5 h-2.5 bg-emerald-400" />
        <div className="absolute bottom-0 w-0.5 h-2.5 bg-emerald-400" />
        <div className="absolute left-0 h-0.5 w-2.5 bg-emerald-400" />
        <div className="absolute right-0 h-0.5 w-2.5 bg-emerald-400" />
      </div>

      {/* DYNAMIC REAL-TIME BOUNDING BOX OVERLAY */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {visibleDetections.map((target) => {
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

          // Visual theme per class
          let borderTheme = 'border-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.35)]';
          let bgTheme = 'bg-rose-500/10';
          let headerBadgeBg = 'bg-rose-500 text-white';

          if (isVehicle) {
            borderTheme = 'border-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.35)]';
            bgTheme = 'bg-cyan-500/10';
            headerBadgeBg = 'bg-cyan-500 text-obsidian font-bold';
          } else if (isObject) {
            borderTheme = 'border-purple-500 shadow-[0_0_15px_rgba(168,85,247,0.35)]';
            bgTheme = 'bg-purple-500/10';
            headerBadgeBg = 'bg-purple-600 text-white';
          } else if (isAnimal) {
            borderTheme = 'border-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.35)]';
            bgTheme = 'bg-amber-500/10';
            headerBadgeBg = 'bg-amber-500 text-obsidian font-bold';
          }

          return (
            <div
              key={target.id}
              onClick={() => onSelectTarget && onSelectTarget(isSelected ? null : target.id)}
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
              {/* Tactical Corner Brackets */}
              <div className="absolute -top-1 -left-1 w-2.5 h-2.5 border-t-2 border-l-2 border-white pointer-events-none" />
              <div className="absolute -top-1 -right-1 w-2.5 h-2.5 border-t-2 border-r-2 border-white pointer-events-none" />
              <div className="absolute -bottom-1 -left-1 w-2.5 h-2.5 border-b-2 border-l-2 border-white pointer-events-none" />
              <div className="absolute -bottom-1 -right-1 w-2.5 h-2.5 border-b-2 border-r-2 border-white pointer-events-none" />

              {/* Target Identification Header - Sleek Compact Single-Line Pill */}
              <div className="absolute -top-6 left-0 flex items-center space-x-1 whitespace-nowrap pointer-events-none">
                <div className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold flex items-center space-x-1 shadow-lg border border-white/20 ${headerBadgeBg}`}>
                  <span>{target.track_id}</span>
                  <span>•</span>
                  <span>{target.class_name.toUpperCase()}</span>
                  <span>({(target.confidence * 100).toFixed(0)}%)</span>
                </div>

                {/* Sub-label inline status pill (eliminates bottom overlapping clutter) */}
                {(target.sub_label || target.details?.behavior || target.details?.anpr_plate) && (
                  <div className="bg-black/90 backdrop-blur-md border border-slate-700/90 px-1.5 py-0.5 rounded text-[8px] font-mono text-slate-200 flex items-center space-x-1 shadow-md">
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

      {/* Bottom Metadata Ribbon */}
      <div className="flex flex-wrap items-center justify-between gap-2 pointer-events-auto">
        <div className="bg-black/80 px-2.5 py-1 rounded-xl backdrop-blur-md border border-emerald-500/20 text-[10px] text-emerald-400">
          <span>COORDS: {coordinates}</span>
        </div>

        {/* Interactive Filter Quick Controls Bar */}
        {showFilters && (
          <div className="flex items-center space-x-1.5 bg-black/80 px-2.5 py-1 rounded-xl backdrop-blur-md border border-slate-800 text-[10px]">
            <span className="text-slate-400 flex items-center space-x-1 mr-1">
              <Filter className="w-3 h-3" />
              <span>HUD LAYERS:</span>
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
          <span>ACTIVE DETECTIONS: {visibleDetections.length}</span>
        </div>
      </div>

    </div>
  );
};
