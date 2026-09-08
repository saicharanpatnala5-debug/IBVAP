"""
IBVAP - WebSocket Real-Time Broadcasting Manager
Handles real-time distribution of alerts, camera status, and threat telemetry to connected dashboards.
"""
from typing import List, Dict, Any
from fastapi import WebSocket
from app.core.logging import logger

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast JSON payload to all connected command dashboards."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_alert(self, message: Dict[str, Any]):
        """Broadcast real-time alert payload."""
        await self.broadcast(message)

    async def broadcast_telemetry(self, message: Dict[str, Any]):
        """Broadcast live telemetry frame."""
        await self.broadcast(message)

ws_manager = WebSocketManager()
manager = ws_manager
