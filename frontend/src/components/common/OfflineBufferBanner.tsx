import React from 'react';
import { WifiOff, RefreshCw, Database, CheckCircle2 } from 'lucide-react';
import { useOfflineSync } from '../../services/offlineSyncService';

export const OfflineBufferBanner: React.FC = () => {
  const { isOffline, bufferedCount, isSyncing, lastSyncTime, batchSync } = useOfflineSync();

  if (!isOffline && bufferedCount === 0) {
    return null;
  }

  return (
    <div className="w-full bg-amber-500/15 border-b border-amber-500/50 backdrop-blur-md px-4 py-2 flex flex-wrap items-center justify-between text-xs font-mono text-amber-200 z-50 animate-fade-in">
      <div className="flex items-center space-x-2.5">
        <div className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping" />
        <WifiOff className="w-4 h-4 text-amber-400 flex-shrink-0" />
        <span className="font-bold tracking-wider text-amber-300">
          LOW CONNECTIVITY — BUFFERING DATA LOCALLY
        </span>
        <span className="hidden sm:inline text-amber-200/80">
          (Fail-Safe ACID Storage active • Zero packet loss)
        </span>
      </div>

      <div className="flex items-center space-x-3 mt-1 sm:mt-0">
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-amber-950/60 border border-amber-500/40 text-amber-300">
          <Database className="w-3.5 h-3.5 text-amber-400" />
          <span className="font-bold">{bufferedCount} Events Buffered</span>
        </div>

        {lastSyncTime && (
          <span className="hidden md:inline text-[11px] text-slate-400 flex items-center space-x-1">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>Last Sync: {lastSyncTime}</span>
          </span>
        )}

        <button
          onClick={() => batchSync()}
          disabled={isSyncing}
          className="px-2.5 py-1 rounded bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/60 text-amber-200 font-bold transition-all flex items-center space-x-1.5 cursor-pointer disabled:opacity-50"
          title="Force flush offline buffer to server"
        >
          <RefreshCw className={`w-3 h-3 text-amber-300 ${isSyncing ? 'animate-spin' : ''}`} />
          <span>{isSyncing ? 'Syncing...' : 'Sync Now'}</span>
        </button>
      </div>
    </div>
  );
};
