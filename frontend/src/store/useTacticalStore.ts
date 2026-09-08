import { useState, useEffect } from 'react';
import { Camera, Alert, Incident } from '../types';
import { MOCK_CAMERAS, MOCK_ALERTS, MOCK_INCIDENTS } from '../services/api';

interface State {
  selectedCameraId: string;
  selectedSector: string;
  threatLevel: 'NORMAL' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  audioAlertsEnabled: boolean;
  sidebarCollapsed: boolean;
  activeIncidentsCount: number;
}

let globalState: State = {
  selectedCameraId: 'CAM-01',
  selectedSector: 'Sector-B',
  threatLevel: 'HIGH',
  audioAlertsEnabled: true,
  sidebarCollapsed: false,
  activeIncidentsCount: 3,
};

const listeners = new Set<(s: State) => void>();

export function setTacticalState(partial: Partial<State>) {
  globalState = { ...globalState, ...partial };
  listeners.forEach((l) => l(globalState));
}

export function useTacticalStore() {
  const [state, setState] = useState<State>(globalState);

  useEffect(() => {
    listeners.add(setState);
    return () => {
      listeners.delete(setState);
    };
  }, []);

  return {
    ...state,
    setSelectedCamera: (id: string) => setTacticalState({ selectedCameraId: id }),
    setSelectedSector: (s: string) => setTacticalState({ selectedSector: s }),
    setThreatLevel: (t: State['threatLevel']) => setTacticalState({ threatLevel: t }),
    toggleAudioAlerts: () => setTacticalState({ audioAlertsEnabled: !globalState.audioAlertsEnabled }),
    toggleSidebar: () => setTacticalState({ sidebarCollapsed: !globalState.sidebarCollapsed }),
  };
}
