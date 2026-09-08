"""
Integration Test: Full SIH 2026 Demo Scenario Pipeline
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_sih_demo_scenario():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Run the full 8-step SIH scenario
        res = await ac.post("/api/demo/run-scenario")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert data["steps_count"] == 8

        # Verify step 7 fused into critical incident
        step_7 = data["scenario_results"][6]
        assert step_7["severity"] == "CRITICAL"
        assert step_7["risk_score"] == 125
        assert "explainability_card" in step_7

        # Verify step 8 predictive handoff
        step_8 = data["scenario_results"][7]
        assert step_8["predicted_next_camera"] == "CAM-03"
        assert step_8["confidence_pct"] >= 75.0

        # Check incidents endpoint returns the fused incident
        inc_res = await ac.get("/api/incidents")
        assert inc_res.status_code == 200
        incidents = inc_res.json()
        assert len(incidents) >= 1

        # Check search endpoint
        search_res = await ac.post("/api/search", json={"query_text": "Perimeter"})
        assert search_res.status_code == 200
        assert search_res.json()["total_found"] >= 1
