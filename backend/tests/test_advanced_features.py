"""
Integration Tests: ANPR, Face Verification, System Health, Audit Trail, and Predictive Handoff
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_anpr_logging_and_search():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        plate_data = {
            "camera_id": "CAM-01",
            "plate_text": "HR26DK8888",
            "ocr_confidence": 0.95,
            "vehicle_class": "truck",
            "vehicle_color": "Blue",
            "direction": "Inward"
        }
        res = await ac.post("/api/anpr/log-sighting", json=plate_data)
        assert res.status_code == 200
        data = res.json()
        assert data["plate_text"] == "HR26DK8888"
        assert data["ocr_confidence"] == 0.95

        list_res = await ac.get("/api/anpr/plates?plate_text=HR26")
        assert list_res.status_code == 200
        plates = list_res.json()
        assert len(plates) >= 1

@pytest.mark.asyncio
async def test_system_health_and_telemetry():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/health/summary")
        assert res.status_code == 200
        health = res.json()
        assert health["system_status"] in ["HEALTHY", "DEGRADED", "CRITICAL"]
        assert health["total_cameras"] >= 4
        assert len(health["camera_health_list"]) >= 4

@pytest.mark.asyncio
async def test_predictive_handoff_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/cameras/CAM-01/predict-handoff")
        assert res.status_code == 200
        handoff = res.json()
        assert handoff["has_prediction"] is True
        assert handoff["handoff"]["predicted_camera_id"] == "CAM-03"

@pytest.mark.asyncio
async def test_audit_logs():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/audit")
        assert res.status_code == 200
        logs = res.json()
        assert isinstance(logs, list)

@pytest.mark.asyncio
async def test_face_sightings_and_watchlist():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        w_res = await ac.get("/api/faces/watchlist")
        assert w_res.status_code == 200
        watchlist = w_res.json()
        assert isinstance(watchlist, list)

        f_res = await ac.get("/api/faces/sightings")
        assert f_res.status_code == 200
        assert isinstance(f_res.json(), list)
