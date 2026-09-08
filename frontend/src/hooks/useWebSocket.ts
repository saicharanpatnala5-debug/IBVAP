import { useEffect, useState } from 'react';
import { alertStream } from '../services/websocket';

export function useWebSocket(onMessage?: (data: any) => void) {
  const [connected, setConnected] = useState(true);

  useEffect(() => {
    alertStream.connect();
    const unsub = alertStream.subscribe((data) => {
      setConnected(true);
      if (onMessage) onMessage(data);
    });

    return () => {
      unsub();
    };
  }, [onMessage]);

  return { connected };
}
