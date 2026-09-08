"""
IBVAP - Database Seeding Script (Idempotent)
Initializes sample cameras, topology edges, virtual zones, users, and watchlists for SIH Demo.
"""
import asyncio
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_db
from app.core.security import hash_password
from app.models.camera import Camera, CameraTopologyEdge
from app.models.zone import Zone
from app.models.user import User
from app.models.face_watchlist import Watchlist
from app.core.logging import logger

async def seed():
    print("Initializing database tables...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        existing_cam = await db.execute(select(Camera))
        if existing_cam.scalars().first():
            print("Database already contains cameras and seed data. Skipping duplication.")
            return

        print("Seeding users...")
        users = [
            User(
                user_id="USR-ADMIN-01",
                username="admin",
                email="admin@ibvap.gov.in",
                full_name="Col. R. K. Sharma (Base Commander)",
                hashed_password=hash_password("admin123"),
                role="admin"
            ),
            User(
                user_id="USR-SUP-01",
                username="supervisor",
                email="supervisor@ibvap.gov.in",
                full_name="Maj. V. Nair (Operations Supervisor)",
                hashed_password=hash_password("super123"),
                role="supervisor"
            ),
            User(
                user_id="USR-OP-01",
                username="operator",
                email="operator@ibvap.gov.in",
                full_name="Subedar A. Singh (CCTV Controller)",
                hashed_password=hash_password("operator123"),
                role="cctv_operator"
            ),
            User(
                user_id="USR-AUD-01",
                username="auditor",
                email="auditor@ibvap.gov.in",
                full_name="Dr. S. Mukherjee (DPDP Compliance Officer)",
                hashed_password=hash_password("auditor123"),
                role="auditor"
            )
        ]
        for u in users:
            db.add(u)

        print("Seeding border cameras...")
        cameras = [
            Camera(
                camera_id="CAM-01",
                name="BOP Alpha - Main Approach Road",
                site="BOP-Alpha",
                sector="Sector-B",
                latitude=28.6139,
                longitude=77.2090,
                stream_url="rtsp://192.168.1.101:554/stream1",
                fps=25.0,
                resolution="1920x1080",
                status="ONLINE",
                is_simulated=True
            ),
            Camera(
                camera_id="CAM-02",
                name="BOP Alpha - North Perimeter Gate",
                site="BOP-Alpha",
                sector="Sector-B",
                latitude=28.6148,
                longitude=77.2098,
                stream_url="rtsp://192.168.1.102:554/stream1",
                fps=25.0,
                resolution="1920x1080",
                status="ONLINE",
                is_simulated=True
            ),
            Camera(
                camera_id="CAM-03",
                name="BOP Alpha - Sensitive Border Fence Red Zone",
                site="BOP-Alpha",
                sector="Sector-B",
                latitude=28.6155,
                longitude=77.2112,
                stream_url="rtsp://192.168.1.103:554/stream1",
                fps=25.0,
                resolution="1920x1080",
                status="ONLINE",
                is_simulated=True
            ),
            Camera(
                camera_id="CAM-07",
                name="BOP Alpha - Inner Installation Strategic Depot",
                site="BOP-Alpha",
                sector="Sector-B",
                latitude=28.6162,
                longitude=77.2125,
                stream_url="rtsp://192.168.1.107:554/stream1",
                fps=25.0,
                resolution="1920x1080",
                status="ONLINE",
                is_simulated=True
            )
        ]
        for c in cameras:
            db.add(c)

        print("Seeding camera graph topology...")
        edges = [
            CameraTopologyEdge(
                from_camera_id="CAM-01",
                to_camera_id="CAM-03",
                transition_probability=0.78,
                min_transit_seconds=15.0,
                max_transit_seconds=45.0,
                distance_meters=60.0
            ),
            CameraTopologyEdge(
                from_camera_id="CAM-01",
                to_camera_id="CAM-02",
                transition_probability=0.22,
                min_transit_seconds=20.0,
                max_transit_seconds=60.0,
                distance_meters=85.0
            ),
            CameraTopologyEdge(
                from_camera_id="CAM-03",
                to_camera_id="CAM-07",
                transition_probability=0.82,
                min_transit_seconds=25.0,
                max_transit_seconds=70.0,
                distance_meters=110.0
            )
        ]
        for e in edges:
            db.add(e)

        print("Seeding virtual fence zones...")
        zones = [
            Zone(
                zone_id="ZONE-RED-01",
                camera_id="CAM-01",
                name="Perimeter Zero-Tolerance Restricted Area",
                zone_type="RED_RESTRICTED",
                polygon_coords=[[0.35, 0.30], [0.75, 0.30], [0.75, 0.85], [0.35, 0.85]],
                alert_level="CRITICAL",
                rules={"dwell_threshold": 15, "direction": "inward"},
                is_active=True
            ),
            Zone(
                zone_id="ZONE-YEL-01",
                camera_id="CAM-01",
                name="Buffer Monitoring Zone",
                zone_type="YELLOW_MONITORING",
                polygon_coords=[[0.10, 0.10], [0.90, 0.10], [0.90, 0.90], [0.10, 0.90]],
                alert_level="MEDIUM",
                rules={"dwell_threshold": 30},
                is_active=True
            )
        ]
        for z in zones:
            db.add(z)

        print("Seeding security watchlists...")
        watchlists = [
            Watchlist(
                category="VEHICLE",
                identifier_code="DL01AB9876",
                name_label="Blacklisted Dark SUV",
                description="Reported in suspicious reconnaissance near Sector B checkpost",
                risk_priority="HIGH"
            ),
            Watchlist(
                category="PERSON",
                identifier_code="POW-4091",
                name_label="Unauthorized Infiltrator Profile #4091",
                description="Cross-border alert issued by intelligence bureau",
                risk_priority="CRITICAL"
            )
        ]
        for w in watchlists:
            db.add(w)

        await db.commit()
        print("Database seeded successfully with realistic SIH demonstration data!")

if __name__ == "__main__":
    asyncio.run(seed())
