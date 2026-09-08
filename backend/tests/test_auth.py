"""
IBVAP - Dedicated Authentication & Authorization Test Suite
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_auth_login_and_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Login with admin account (or fallback test user)
        resp = await client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        if resp.status_code != 200:
            await client.post("/api/auth/register", json={
                "username": "auth_test_user",
                "email": "auth_test@ibvap.gov.in",
                "full_name": "Auth Test User",
                "password": "AdminSecurePassword2026!",
                "role": "admin"
            })
            resp = await client.post(
                "/api/auth/login",
                data={"username": "auth_test_user", "password": "AdminSecurePassword2026!"}
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "admin"
        
        token = data["access_token"]

        # 2. Access /api/auth/me
        me_resp = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["username"] in ["admin", "operator_demo", "auth_test_user"]

@pytest.mark.asyncio
async def test_auth_invalid_credentials():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "WrongPassword!"}
        )
        assert resp.status_code == 401
