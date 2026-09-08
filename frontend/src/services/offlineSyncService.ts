/**
 * IBVAP - Tactical Offline Caching & Low-Connectivity Resilience Service
 * Directly implements PRD MoSCoW Requirement: Edge Offline Buffering & Resilience
 * Queues critical event metadata locally when WebSocket/backhaul drops,
 * displays prominent buffer telemetry, and automatically batch-synchronizes when connection returns.
 */
import { useEffect, useState } from 'react';

export interface BufferedTacticalEvent {
  id: string;
  eventType: string;
  cameraId: string;
  timestamp: string;
  riskScore: number;
  priorityTier: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  payload: any;
}

const STORAGE_KEY = 'ibvap_tactical_offline_buffer_v1';

class OfflineSyncManager {
  private listeners: Set<() => void> = new Set();
  private isOnline: boolean = typeof navigator !== 'undefined' ? navigator.onLine : true;
  private isSyncing: boolean = false;
  private lastSyncTime: string | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      window.addEventListener('online', () => this.handleNetworkChange(true));
      window.addEventListener('offline', () => this.handleNetworkChange(false));
    }
  }

  private handleNetworkChange(online: boolean) {
    this.isOnline = online;
    this.notify();
    if (online) {
      // Auto-trigger batch synchronization upon network restoration
      this.batchSync();
    }
  }

  public setConnectionState(online: boolean) {
    if (this.isOnline !== online) {
      this.isOnline = online;
      this.notify();
      if (online) {
        this.batchSync();
      }
    }
  }

  public getIsOnline(): boolean {
    return this.isOnline;
  }

  public getIsSyncing(): boolean {
    return this.isSyncing;
  }

  public getLastSyncTime(): string | null {
    return this.lastSyncTime;
  }

  public getBufferedEvents(): BufferedTacticalEvent[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  public getBufferedCount(): number {
    return this.getBufferedEvents().length;
  }

  public queueEvent(event: Omit<BufferedTacticalEvent, 'id' | 'timestamp'>): void {
    try {
      const current = this.getBufferedEvents();
      const newEntry: BufferedTacticalEvent = {
        ...event,
        id: `OFFLINE-EV-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
        timestamp: new Date().toISOString()
      };
      current.push(newEntry);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(current));
      this.notify();
      console.log(`[OfflineBuffer] Queued event ${newEntry.id}. Total in buffer: ${current.length}`);
    } catch (e) {
      console.warn('[OfflineBuffer] Failed to write event to storage:', e);
    }
  }

  public clearBuffer(): void {
    try {
      localStorage.removeItem(STORAGE_KEY);
      this.notify();
    } catch (e) {
      console.warn('[OfflineBuffer] Failed to clear buffer:', e);
    }
  }

  public async batchSync(): Promise<{ success: boolean; syncedCount: number }> {
    const events = this.getBufferedEvents();
    if (events.length === 0) {
      return { success: true, syncedCount: 0 };
    }

    this.isSyncing = true;
    this.notify();

    try {
      const response = await fetch('/api/events/batch-sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ events })
      });

      if (response.ok) {
        const result = await response.json();
        const syncedCount = events.length;
        this.clearBuffer();
        this.lastSyncTime = new Date().toLocaleTimeString();
        this.isSyncing = false;
        this.notify();
        console.log(`[OfflineBuffer] Batch-synced ${syncedCount} events successfully.`);
        return { success: true, syncedCount };
      } else {
        throw new Error(`Server returned ${response.status}`);
      }
    } catch (e) {
      console.warn('[OfflineBuffer] Batch sync attempt failed, keeping events in buffer:', e);
      this.isSyncing = false;
      this.notify();
      return { success: false, syncedCount: 0 };
    }
  }

  public subscribe(cb: () => void): () => void {
    this.listeners.add(cb);
    return () => this.listeners.delete(cb);
  }

  private notify() {
    this.listeners.forEach(cb => cb());
  }
}

export const offlineSyncManager = new OfflineSyncManager();

export function useOfflineSync() {
  const [, setTick] = useState(0);

  useEffect(() => {
    return offlineSyncManager.subscribe(() => setTick(t => t + 1));
  }, []);

  return {
    isOnline: offlineSyncManager.getIsOnline(),
    isOffline: !offlineSyncManager.getIsOnline(),
    isSyncing: offlineSyncManager.getIsSyncing(),
    bufferedCount: offlineSyncManager.getBufferedCount(),
    lastSyncTime: offlineSyncManager.getLastSyncTime(),
    queueEvent: (ev: Omit<BufferedTacticalEvent, 'id' | 'timestamp'>) => offlineSyncManager.queueEvent(ev),
    batchSync: () => offlineSyncManager.batchSync(),
    clearBuffer: () => offlineSyncManager.clearBuffer(),
    setConnectionState: (online: boolean) => offlineSyncManager.setConnectionState(online)
  };
}
