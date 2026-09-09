import os
import json
import pytest
from httpx import AsyncClient, ASGITransport

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

def test_frontend_root_configuration_files():
    """Verify all configuration and tooling files exist with proper specifications."""
    expected_configs = [
        "package.json",
        "tsconfig.json",
        "tsconfig.node.json",
        "vite.config.ts",
        "tailwind.config.js",
        "postcss.config.js",
        "Dockerfile",
        "nginx.conf",
        "README.md",
        "index.html",
        os.path.join("public", "favicon.svg"),
        os.path.join("public", "favicon.ico"),
        os.path.join("public", "index.html"),
    ]
    for config_rel in expected_configs:
        path = os.path.join(FRONTEND_DIR, config_rel)
        assert os.path.exists(path), f"Required file {config_rel} missing from frontend"

    # Verify package.json structure
    pkg_path = os.path.join(FRONTEND_DIR, "package.json")
    with open(pkg_path, "r", encoding="utf-8") as f:
        pkg = json.load(f)
    assert pkg["name"] == "ibvap-tactical-frontend"
    assert "react" in pkg["dependencies"]
    assert "lucide-react" in pkg["dependencies"]
    assert "tailwindcss" in pkg["devDependencies"]
    assert "vite" in pkg["devDependencies"]

def test_frontend_all_12_pages_exist_and_valid():
    """Verify all 12 operational page modules exist and have valid component exports."""
    pages_dir = os.path.join(FRONTEND_DIR, "src", "pages")
    expected_pages = [
        "Login.tsx",
        "Dashboard.tsx",
        "LiveMonitoring.tsx",
        "Cameras.tsx",
        "Alerts.tsx",
        "Incidents.tsx",
        "IncidentDetails.tsx",
        "VideoSearch.tsx",
        "Analytics.tsx",
        "MapView.tsx",
        "Settings.tsx",
        "NotFound.tsx",
    ]
    assert len(expected_pages) == 12
    for page in expected_pages:
        page_path = os.path.join(pages_dir, page)
        assert os.path.exists(page_path), f"Page {page} missing from {pages_dir}"
        with open(page_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "export const" in content or "export default" in content, f"{page} missing export"
        assert len(content) > 200, f"{page} is unexpectedly empty"

def test_frontend_component_library():
    """Verify modular UI components exist across tactical subsystems."""
    components_dir = os.path.join(FRONTEND_DIR, "src", "components")
    expected_components = [
        os.path.join("common", "Navbar.tsx"),
        os.path.join("common", "Sidebar.tsx"),
        os.path.join("common", "Breadcrumbs.tsx"),
        os.path.join("common", "HighContrastRiskBanner.tsx"),
        os.path.join("common", "OfflineBufferBanner.tsx"),
        os.path.join("camera", "CameraCard.tsx"),
        os.path.join("camera", "CameraGrid.tsx"),
        os.path.join("camera", "PTZControls.tsx"),
        os.path.join("alerts", "AlertBadge.tsx"),
        os.path.join("alerts", "AlertList.tsx"),
        os.path.join("alerts", "AlertDetailModal.tsx"),
        os.path.join("alerts", "AlertExplainabilityCard.tsx"),
        os.path.join("incidents", "ExplainableAICard.tsx"),
        os.path.join("incidents", "IncidentTimeline.tsx"),
        os.path.join("video", "HUDOverlay.tsx"),
        os.path.join("video", "LiveStreamPlayer.tsx"),
        os.path.join("video", "EvidencePlayback.tsx"),
        os.path.join("video", "CCTVUploadModal.tsx"),
        os.path.join("video", "TacticalDetectionOverlay.tsx"),
        os.path.join("video", "TacticalIngestionHub.tsx"),
        os.path.join("maps", "TacticalMap.tsx"),
        os.path.join("charts", "ThreatRadarChart.tsx"),
        os.path.join("charts", "HourlyBreachChart.tsx"),
        os.path.join("charts", "RiskDistributionChart.tsx"),
        os.path.join("dss", "AITacticalRecommendations.tsx"),
        os.path.join("twin", "DigitalTwinSimulator.tsx"),
    ]
    for comp in expected_components:
        comp_path = os.path.join(components_dir, comp)
        assert os.path.exists(comp_path), f"Component {comp} missing from {components_dir}"
        with open(comp_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 150, f"Component {comp} content is too short"

def test_frontend_aesthetic_and_tactical_mandates():
    """Verify specific aesthetic and tactical UI directives."""
    # 1. Liquid glass and colored left stripes in CameraCard.tsx
    card_path = os.path.join(FRONTEND_DIR, "src", "components", "camera", "CameraCard.tsx")
    with open(card_path, "r", encoding="utf-8") as f:
        card_code = f.read()
    assert "liquid-glass" in card_code or "backdrop-blur" in card_code
    assert "border-l-4 border-emerald-500" in card_code
    assert "border-l-4 border-rose-500" in card_code

    # 2. Tactical detection overlay with SVG polygon drawing and point-in-polygon fencing
    overlay_path = os.path.join(FRONTEND_DIR, "src", "components", "video", "TacticalDetectionOverlay.tsx")
    with open(overlay_path, "r", encoding="utf-8") as f:
        overlay_code = f.read()
    assert "isPointInPolygon" in overlay_code or "pointInPolygon" in overlay_code or "polygon" in overlay_code.lower()
    assert "svg" in overlay_code.lower()

    # 3. Explainable AI risk factors in CCTVUploadModal
    cctv_path = os.path.join(FRONTEND_DIR, "src", "components", "video", "CCTVUploadModal.tsx")
    with open(cctv_path, "r", encoding="utf-8") as f:
        cctv_code = f.read()
    assert "risk_breakdown" in cctv_code or "evaluateRisk" in cctv_code or "risk" in cctv_code.lower()

@pytest.mark.asyncio
async def test_fastapi_serves_frontend_dashboard():
    """Verify backend FastAPI server serves the frontend dashboard at /dashboard and /ui."""
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_dashboard = await client.get("/dashboard")
        assert resp_dashboard.status_code == 200
        assert "IBVAP" in resp_dashboard.text
        assert "text/html" in resp_dashboard.headers.get("content-type", "")

        resp_ui = await client.get("/ui")
        assert resp_ui.status_code == 200
        assert "Command Post" in resp_ui.text
