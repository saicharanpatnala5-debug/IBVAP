"""
IBVAP - Dedicated Events, Detections & Tracks Test Suite
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_events_detections_and_tracks():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Auth login
        login_resp = await client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        if login_resp.status_code != 200:
            await client.post("/api/auth/register", json={
                "username": "evt_test_user",
                "email": "evt_test@ibvap.gov.in",
                "full_name": "Event Test User",
                "password": "AdminSecurePassword2026!",
                "role": "admin"
            })
            login_resp = await client.post(
                "/api/auth/login",
                data={"username": "evt_test_user", "password": "AdminSecurePassword2026!"}
            )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Query events
        evt_resp = await client.get("/api/events", headers=headers)
        assert evt_resp.status_code == 200

        # 2. Query detections
        det_resp = await client.get("/api/detections", headers=headers)
        assert det_resp.status_code == 200
        dets = det_resp.json()
        assert len(dets) >= 1

        # 3. Query classes
        cls_resp = await client.get("/api/detections/classes", headers=headers)
        assert cls_resp.status_code == 200
        assert "person" in cls_resp.json()["classes"]

        # 4. Query tracks
        trk_resp = await client.get("/api/tracks", headers=headers)
        assert trk_resp.status_code == 200
        assert len(trk_resp.json()) >= 1
