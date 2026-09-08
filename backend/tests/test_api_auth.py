"""
Unit Tests: Authentication and JWT Security
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "OPERATIONAL"
        assert "IBVAP" in data["platform"]

@pytest.mark.asyncio
async def test_user_registration_and_login():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register new operator
        username = "test_guard_1"
        reg_res = await ac.post("/api/auth/register", json={
            "username": username,
            "email": "guard1@ibvap.gov.in",
            "full_name": "Test Border Guard",
            "password": "securepassword123",
            "role": "cctv_operator"
        })
        assert reg_res.status_code in [200, 400] # 200 or already registered

        # Login
        login_res = await ac.post("/api/auth/login", data={
            "username": username,
            "password": "securepassword123"
        })
        assert login_res.status_code == 200
        tokens = login_res.json()
        assert "access_token" in tokens
        assert tokens["token_type"] == "bearer"
