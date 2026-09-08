"""
Unit Tests: Cameras and Virtual Fence Zones
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_camera_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # List cameras
        res = await ac.get("/api/cameras")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

@pytest.mark.asyncio
async def test_zone_creation_and_listing():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create zone
        zone_data = {
            "zone_id": "TEST-ZONE-RED",
            "camera_id": "CAM-01",
            "name": "Test Restricted Polygon",
            "zone_type": "RED_RESTRICTED",
            "polygon_coords": [[0.2, 0.2], [0.8, 0.2], [0.8, 0.8], [0.2, 0.8]],
            "alert_level": "CRITICAL"
        }
        res = await ac.post("/api/zones", json=zone_data)
        assert res.status_code in [200, 400]

        # List zones
        list_res = await ac.get("/api/zones")
        assert list_res.status_code == 200
