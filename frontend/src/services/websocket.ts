export class TacticalWebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private listeners: Set<(data: any) => void> = new Set();
  private isIntentionalClose = false;

  constructor(path: string = '/ws/alerts') {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    this.url = `${protocol}//${host}${path}`;
  }

  connect() {
    this.isIntentionalClose = false;
    try {
      this.ws = new WebSocket(this.url);
      this.ws.onopen = () => {
        console.log('[IBVAP WS] Connected to Tactical Stream');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          this.listeners.forEach((cb) => cb(payload));
        } catch (e) {
          console.error('[IBVAP WS] Message parse error', e);
        }
      };

      this.ws.onclose = () => {
        if (!this.isIntentionalClose) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = (err) => {
        console.warn('[IBVAP WS] Connection issue, retrying...', err);
        this.ws?.close();
      };
    } catch (err) {
      console.warn('[IBVAP WS] Offline mode or proxy inactive', err);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(1.5, this.reconnectAttempts), 15000);
      setTimeout(() => this.connect(), delay);
    }
  }

  subscribe(callback: (data: any) => void): () => void {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  disconnect() {
    this.isIntentionalClose = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const alertStream = new TacticalWebSocketClient('/ws/alerts');
