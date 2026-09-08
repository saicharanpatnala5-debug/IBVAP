import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Send, 
  Edit3, 
  CheckCircle2, 
  Radio, 
  Camera, 
  Lightbulb, 
  Clock, 
  UserCheck, 
  AlertTriangle 
} from 'lucide-react';

export interface TacticalRecommendation {
  id: string;
  title: string;
  description: string;
  priority: 'CRITICAL' | 'HIGH' | 'MODERATE';
  iconType: 'dispatch' | 'camera' | 'deterrent';
  recommendedBy: string;
  timestamp: string;
  status: 'PENDING' | 'APPROVED' | 'MODIFIED' | 'REJECTED';
  modifiedNotes?: string;
}

interface AITacticalRecommendationsProps {
  threatDetected?: boolean;
  threatTitle?: string;
  threatScore?: number;
  cameraId?: string;
  onActionDispatched?: (actionId: string, actionName: string, status: string) => void;
}

const DEFAULT_RECOMMENDATIONS: TacticalRecommendation[] = [
  {
    id: 'REC-01',
    title: 'Dispatch Sector B Quick Reaction Team (QRT)',
    description: 'Direct QRT-02 patrol vehicle to coordinate BOP-Alpha North perimeter. Intercept ETA: 2m 15s along inward infiltration vector.',
    priority: 'CRITICAL',
    iconType: 'dispatch',
    recommendedBy: 'IBVAP Threat Heuristics Engine',
    timestamp: 'Just now',
    status: 'PENDING'
  },
  {
    id: 'REC-02',
    title: 'Engage Secondary Optical PTZ & Handoff Tracking',
    description: 'Slew Camera CAM-03 to boundary intercept coordinate [X: 0.65, Y: 0.48]. Lock 30x optical zoom on primary moving target.',
    priority: 'HIGH',
    iconType: 'camera',
    recommendedBy: 'Predictive Multi-Camera Handoff Graph',
    timestamp: 'Just now',
    status: 'PENDING'
  },
  {
    id: 'REC-03',
    title: 'Activate Perimeter Floodlights & Acoustic Strobe',
    description: 'Energize high-intensity LED floodlights along Fence Segment Alpha-04 to strip night cover and deploy directional audio deterrent.',
    priority: 'MODERATE',
    iconType: 'deterrent',
    recommendedBy: 'Automated Countermeasure Subsystem',
    timestamp: 'Just now',
    status: 'PENDING'
  }
];

export const AITacticalRecommendations: React.FC<AITacticalRecommendationsProps> = ({
  threatDetected = true,
  threatTitle = 'Perimeter Breach Detected',
  threatScore = 118,
  cameraId = 'CAM-01',
  onActionDispatched
}) => {
  const [recommendations, setRecommendations] = useState<TacticalRecommendation[]>(DEFAULT_RECOMMENDATIONS);
  const [editingRecId, setEditingRecId] = useState<string | null>(null);
  const [customNote, setCustomNote] = useState<string>('');

  const handleApprove = (id: string) => {
    setRecommendations(prev => prev.map(rec => {
      if (rec.id === id) {
        const updated = { ...rec, status: 'APPROVED' as const };
        if (onActionDispatched) {
          onActionDispatched(rec.id, rec.title, 'APPROVED');
        }
        return updated;
      }
      return rec;
    }));
  };

  const handleStartModify = (rec: TacticalRecommendation) => {
    setEditingRecId(rec.id);
    setCustomNote(rec.modifiedNotes || rec.description);
  };

  const handleSaveModify = (id: string) => {
    setRecommendations(prev => prev.map(rec => {
      if (rec.id === id) {
        const updated = { 
          ...rec, 
          status: 'MODIFIED' as const,
          modifiedNotes: customNote 
        };
        if (onActionDispatched) {
          onActionDispatched(rec.id, rec.title, 'MODIFIED');
        }
        return updated;
      }
      return rec;
    }));
    setEditingRecId(null);
  };

  const getPriorityBadge = (p: TacticalRecommendation['priority']) => {
    switch (p) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      default:
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40';
    }
  };

  const getIcon = (type: TacticalRecommendation['iconType']) => {
    switch (type) {
      case 'dispatch':
        return <Send className="w-4 h-4 text-rose-400" />;
      case 'camera':
        return <Camera className="w-4 h-4 text-cyan-400" />;
      case 'deterrent':
        return <Lightbulb className="w-4 h-4 text-amber-400" />;
    }
  };

  return (
    <div className="rounded-2xl liquid-glass border border-slate-800 p-4 space-y-4 shadow-2xl animate-fade-in font-mono">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/40 flex items-center justify-center">
            <ShieldCheck className="w-4 h-4 text-emerald-400 animate-pulse" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              AI Tactical Recommendations
            </h3>
            <p className="text-[10px] text-emerald-400 font-semibold">
              Decision Support System (DSS) • Human-in-the-Loop (HITL)
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-1.5 px-2 py-1 rounded bg-slate-900/80 border border-slate-700 text-[10px] text-slate-300">
          <Radio className="w-3 h-3 text-emerald-400 animate-pulse" />
          <span>Active Feed</span>
        </div>
      </div>

      {/* Threat Context Banner */}
      {threatDetected && (
        <div className="rounded-xl p-3 bg-rose-500/10 border border-rose-500/30 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0 animate-bounce" />
            <div>
              <span className="text-white font-bold block">{threatTitle}</span>
              <span className="text-[10px] text-rose-300">Source: {cameraId} • Risk Score: {threatScore} / 120+</span>
            </div>
          </div>
          <span className="text-[9px] uppercase tracking-widest px-2 py-0.5 rounded bg-rose-500 text-slate-950 font-black">
            Action Needed
          </span>
        </div>
      )}

      {/* Recommendations List */}
      <div className="space-y-3">
        {recommendations.map((rec) => {
          const isPending = rec.status === 'PENDING';
          const isApproved = rec.status === 'APPROVED';
          const isModified = rec.status === 'MODIFIED';

          return (
            <div
              key={rec.id}
              className={`rounded-xl p-3.5 border transition-all ${
                isApproved
                  ? 'bg-emerald-500/5 border-emerald-500/40'
                  : isModified
                  ? 'bg-amber-500/5 border-amber-500/40'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              {/* Item Header */}
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 rounded-lg bg-slate-800/80 flex items-center justify-center flex-shrink-0">
                    {getIcon(rec.iconType)}
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">{rec.title}</h4>
                    <span className="text-[9px] text-slate-400">{rec.recommendedBy}</span>
                  </div>
                </div>
                <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border uppercase flex-shrink-0 ${getPriorityBadge(rec.priority)}`}>
                  {rec.priority}
                </span>
              </div>

              {/* Item Body / Modifier */}
              {editingRecId === rec.id ? (
                <div className="space-y-2 my-2">
                  <label className="text-[10px] text-slate-400 block font-bold">
                    MODIFY TACTICAL PARAMETERS:
                  </label>
                  <textarea
                    value={customNote}
                    onChange={(e) => setCustomNote(e.target.value)}
                    rows={2}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  />
                  <div className="flex justify-end space-x-2">
                    <button
                      onClick={() => setEditingRecId(null)}
                      className="px-2 py-1 rounded bg-slate-800 text-slate-400 text-[10px] hover:text-white cursor-pointer"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleSaveModify(rec.id)}
                      className="px-3 py-1 rounded bg-amber-500 text-slate-950 font-bold text-[10px] hover:bg-amber-400 cursor-pointer"
                    >
                      Authorize Modified Action
                    </button>
                  </div>
                </div>
              ) : (
                <p className="text-[11px] text-slate-300 leading-relaxed mb-3">
                  {rec.modifiedNotes ? (
                    <span>
                      <strong className="text-amber-400 block mb-0.5">Operator Modified Order:</strong>
                      {rec.modifiedNotes}
                    </span>
                  ) : (
                    rec.description
                  )}
                </p>
              )}

              {/* Status or HITL Buttons */}
              {isPending && editingRecId !== rec.id && (
                <div className="flex items-center space-x-2 pt-2 border-t border-slate-800/80">
                  <button
                    onClick={() => handleApprove(rec.id)}
                    className="flex-1 py-1.5 px-3 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center space-x-1.5 shadow-md shadow-emerald-500/20 cursor-pointer"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Approve</span>
                  </button>

                  <button
                    onClick={() => handleStartModify(rec)}
                    className="py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-bold text-xs transition-colors flex items-center justify-center space-x-1 cursor-pointer"
                  >
                    <Edit3 className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Modify</span>
                  </button>
                </div>
              )}

              {isApproved && (
                <div className="flex items-center space-x-1.5 text-emerald-400 text-[10px] font-bold pt-1 border-t border-emerald-500/20">
                  <UserCheck className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                  <span>Authorized by Operator (HITL Certified • Dispatched)</span>
                </div>
              )}

              {isModified && (
                <div className="flex items-center space-x-1.5 text-amber-400 text-[10px] font-bold pt-1 border-t border-amber-500/20">
                  <UserCheck className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                  <span>Authorized with Operator Modifications • Dispatched</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* HITL Audit Notice */}
      <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800 text-[9px] text-slate-400 flex items-center justify-between">
        <span className="flex items-center space-x-1">
          <Clock className="w-3 h-3 text-cyan-400" />
          <span>Statutory Compliance: DPDP Act 2023 & MHA Surveillance SOP</span>
        </span>
        <span className="text-emerald-400 font-bold">100% HITL</span>
      </div>
    </div>
  );
};
