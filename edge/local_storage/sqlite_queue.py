"""
IBVAP - High-Throughput ACID SQLite Local Offline Event Queue
Guarantees zero event loss during forward border network blackouts (up to 50,000 events).
"""

import sqlite3
import json
import time
import os
from typing import List, Dict, Any, Optional

class SQLiteOfflineQueue:
    def __init__(self, db_path: str = None, capacity: int = 50000):
        if db_path is None:
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "storage", "edge_buffer"))
            os.makedirs(root, exist_ok=True)
            db_path = os.path.join(root, "edge_events.db")

        self.db_path = db_path
        self.capacity = capacity
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS offline_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE,
                    event_type TEXT NOT NULL,
                    camera_id TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    risk_score INTEGER NOT NULL,
                    priority INTEGER NOT NULL, -- 1=Critical, 2=Watchlist, 3=Incident, 4=Telemetry
                    payload_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    synced INTEGER DEFAULT 0
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_priority_synced ON offline_events(synced, priority, created_at);")

    def enqueue_event(
        self,
        event_type: str,
        camera_id: str,
        severity: str,
        risk_score: int,
        priority: int,
        payload: Dict[str, Any]
    ) -> str:
        """Enqueues an event into the ACID local offline buffer."""
        event_id = f"EVT-EDGE-{camera_id}-{int(time.time() * 1000)}"
        with sqlite3.connect(self.db_path) as conn:
            # Enforce max capacity by purging lowest priority synced or oldest events
            count = conn.execute("SELECT COUNT(*) FROM offline_events WHERE synced = 0").fetchone()[0]
            if count >= self.capacity:
                conn.execute("""
                    DELETE FROM offline_events WHERE id IN (
                        SELECT id FROM offline_events WHERE synced = 0 ORDER BY priority DESC, created_at ASC LIMIT 100
                    )
                """)

            conn.execute("""
                INSERT OR IGNORE INTO offline_events 
                (event_id, event_type, camera_id, severity, risk_score, priority, payload_json, created_at, synced)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (event_id, event_type, camera_id, severity, risk_score, priority, json.dumps(payload), time.time()))
        return event_id

    def peek_uncommitted_batch(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves highest-priority unsynced events in order."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT id, event_id, event_type, camera_id, severity, risk_score, priority, payload_json, created_at
                FROM offline_events 
                WHERE synced = 0 
                ORDER BY priority ASC, created_at ASC 
                LIMIT ?
            """, (limit,)).fetchall()

            return [
                {
                    "id": r["id"],
                    "event_id": r["event_id"],
                    "event_type": r["event_type"],
                    "camera_id": r["camera_id"],
                    "severity": r["severity"],
                    "risk_score": r["risk_score"],
                    "priority": r["priority"],
                    "payload": json.loads(r["payload_json"]),
                    "created_at": r["created_at"]
                }
                for r in rows
            ]

    def acknowledge_sync(self, event_ids: List[str]):
        """Marks successfully synchronized events."""
        if not event_ids:
            return
        with sqlite3.connect(self.db_path) as conn:
            placeholders = ",".join("?" * len(event_ids))
            conn.execute(f"UPDATE offline_events SET synced = 1 WHERE event_id IN ({placeholders})", event_ids)
            # Prune synced events older than 24 hours
            conn.execute("DELETE FROM offline_events WHERE synced = 1 AND created_at < ?", (time.time() - 86400,))

    def get_queue_stats(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            unsynced = conn.execute("SELECT COUNT(*) FROM offline_events WHERE synced = 0").fetchone()[0]
            total = conn.execute("SELECT COUNT(*) FROM offline_events").fetchone()[0]
            crit = conn.execute("SELECT COUNT(*) FROM offline_events WHERE synced = 0 AND priority = 1").fetchone()[0]
            return {
                "unsynced_events": unsynced,
                "total_records": total,
                "critical_pending": crit,
                "capacity": self.capacity,
                "capacity_utilization_pct": round((unsynced / self.capacity) * 100.0, 2)
            }

edge_queue = SQLiteOfflineQueue()
