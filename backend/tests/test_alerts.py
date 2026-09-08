"""
IBVAP - Dedicated Alerts, Vehicles & Analytics Test Suite
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.notification_service import notification_service

@pytest.mark.asyncio
async def test_alerts_and_analytics():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Auth login
        login_resp = await client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        if login_resp.status_code != 200:
            await client.post("/api/auth/register", json={
                "username": "alt_test_user",
                "email": "alt_test@ibvap.gov.in",
                "full_name": "Alert Test User",
                "password": "AdminSecurePassword2026!",
                "role": "admin"
            })
            login_resp = await client.post(
                "/api/auth/login",
                data={"username": "alt_test_user", "password": "AdminSecurePassword2026!"}
            )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Query alerts
        alt_resp = await client.get("/api/alerts", headers=headers)
        assert alt_resp.status_code == 200

        # 2. Query vehicles
        veh_resp = await client.get("/api/vehicles", headers=headers)
        assert veh_resp.status_code == 200
        assert len(veh_resp.json()) >= 1

        # 3. Query analytics summary
        ana_resp = await client.get("/api/analytics/summary", headers=headers)
        assert ana_resp.status_code == 200
        data = ana_resp.json()
        assert data["active_border_cameras"] >= 1
        assert "ELEVATED_DEFENSE_STATUS" in data["system_security_state"]

        # 4. Test NotificationService direct dispatch
        notified = await notification_service.notify_alert(
            alert_data={"camera_id": "CAM-01", "summary": "Perimeter intrusion alert"},
            incident_id="INC-20260906-001",
            severity="CRITICAL"
        )
        assert notified is True
