"""
IBVAP - Dedicated Camera & Stream Test Suite
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_camera_and_stream_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Auth login
        login_resp = await client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        if login_resp.status_code != 200:
            await client.post("/api/auth/register", json={
                "username": "cam_test_user",
                "email": "cam_test@ibvap.gov.in",
                "full_name": "Cam Test User",
                "password": "AdminSecurePassword2026!",
                "role": "admin"
            })
            login_resp = await client.post(
                "/api/auth/login",
                data={"username": "cam_test_user", "password": "AdminSecurePassword2026!"}
            )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Register camera if needed & list cameras
        await client.post("/api/cameras", json={
            "camera_id": "CAM-01",
            "name": "Approach Road North",
            "stream_url": "rtsp://127.0.0.1:8554/cam01",
            "location": "North Approach",
            "latitude": 27.1234,
            "longitude": 84.5678,
            "camera_type": "optical_ptz",
            "status": "online"
        }, headers=headers)

        cam_resp = await client.get("/api/cameras", headers=headers)
        assert cam_resp.status_code == 200
        cameras = cam_resp.json()
        assert len(cameras) >= 1

        # 2. Streams endpoint
        stream_resp = await client.get("/api/streams", headers=headers)
        assert stream_resp.status_code == 200
        streams = stream_resp.json()
        assert len(streams) >= 1
        assert streams[0]["status"] == "ONLINE"

        # 3. Stream restart
        restart_resp = await client.post("/api/streams/CAM-01/restart", headers=headers)
        assert restart_resp.status_code == 200
        assert restart_resp.json()["status"] == "RESTARTING"
