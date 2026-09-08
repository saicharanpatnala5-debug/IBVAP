import { useState, useEffect, useCallback } from 'react';
import { Alert } from '../types';
import { fetchAlerts } from '../services/api';

// Global shared state for alerts - starts ENTIRELY EMPTY (0 alerts on boot)
let globalAlerts: Alert[] = [];
let isInitialized = false;
let wsConnected = false;
const listeners = new Set<(alerts: Alert[]) => void>();

function notifyListeners() {
  const snapshot = [...globalAlerts];
  listeners.forEach((listener) => listener(snapshot));
}

/**
 * Push a new real-time alert dynamically from live video perception or WebSocket
 */
export function pushLiveAlert(alert: Alert) {
  // Guard against duplicate alerts for same alert_id
  if (globalAlerts.some((a) => a.alert_id === alert.alert_id)) {
    return;
  }
  globalAlerts = [alert, ...globalAlerts];
  notifyListeners();
}

/**
 * Set the entire alerts array
 */
export function setGlobalAlerts(updater: Alert[] | ((prev: Alert[]) => Alert[])) {
  if (typeof updater === 'function') {
    globalAlerts = updater(globalAlerts);
  } else {
    globalAlerts = updater;
  }
  notifyListeners();
}

export function clearAllAlerts() {
  globalAlerts = [];
  notifyListeners();
}

function initWebSocketListener() {
  if (wsConnected || typeof window === 'undefined') return;
  try {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname || 'localhost';
    const ws = new WebSocket(`${protocol}//${host}:8000/ws/alerts`);
    wsConnected = true;

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload && (payload.alert_id || payload.type === 'ALERT')) {
          const alertData: Alert = {
            alert_id: payload.alert_id || `ALT-${Date.now()}`,
            camera_id: payload.camera_id || 'CAM-01',
            severity: payload.severity || 'HIGH',
            rule_triggered: payload.rule_triggered || payload.title || 'PERIMETER_BREACH',
            message: payload.message || payload.description || 'Live threat detection threshold exceeded',
            risk_score: payload.risk_score || payload.score || 85,
            status: 'ACTIVE',
            created_at: payload.created_at || new Date().toISOString(),
            confidence: payload.confidence || 0.94,
          };
          pushLiveAlert(alertData);
        }
      } catch {
        // ignore non-json messages
      }
    };

    ws.onclose = () => {
      wsConnected = false;
      setTimeout(initWebSocketListener, 5000);
    };

    ws.onerror = () => {
      ws.close();
    };
  } catch {
    wsConnected = false;
  }
}

export function useAlerts() {
  const [alerts, setLocalAlerts] = useState<Alert[]>(globalAlerts);
  const [loading, setLoading] = useState<boolean>(!isInitialized);

  useEffect(() => {
    listeners.add(setLocalAlerts);

    if (!isInitialized) {
      isInitialized = true;
      fetchAlerts()
        .then((data) => {
          globalAlerts = data || [];
          notifyListeners();
          setLoading(false);
        })
        .catch(() => {
          globalAlerts = [];
          notifyListeners();
          setLoading(false);
        });

      initWebSocketListener();
    }

    return () => {
      listeners.delete(setLocalAlerts);
    };
  }, []);

  const updateAlerts = useCallback((updater: Alert[] | ((prev: Alert[]) => Alert[])) => {
    setGlobalAlerts(updater);
  }, []);

  return {
    alerts,
    loading,
    setAlerts: updateAlerts,
    pushLiveAlert,
    clearAllAlerts,
  };
}
