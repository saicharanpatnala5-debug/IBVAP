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

def test_frontend_all_16_pages_exist_and_valid():
    """Verify all 16 required page modules exist and have valid component exports."""
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
        "About.tsx",
        "Contact.tsx",
        "Waitlist.tsx",
        "ThankYou.tsx",
        "NotFound.tsx",
    ]
    assert len(expected_pages) == 16
    for page in expected_pages:
        page_path = os.path.join(pages_dir, page)
        assert os.path.exists(page_path), f"Page {page} missing from {pages_dir}"
        with open(page_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "export const" in content or "export default" in content, f"{page} missing export"
        assert len(content) > 200, f"{page} is unexpectedly empty"

def test_frontend_component_library():
    """Verify all 25 modular UI components exist across their respective subsystems."""
    components_dir = os.path.join(FRONTEND_DIR, "src", "components")
    expected_components = [
        os.path.join("common", "Navbar.tsx"),
        os.path.join("common", "Sidebar.tsx"),
        os.path.join("common", "Breadcrumbs.tsx"),
        os.path.join("common", "CookieConsent.tsx"),
        os.path.join("common", "PricingTiers.tsx"),
        os.path.join("common", "FeatureCards.tsx"),
        os.path.join("common", "BentoGrid.tsx"),
        os.path.join("common", "Testimonials.tsx"),
        os.path.join("common", "CTASection.tsx"),
        os.path.join("common", "SEOHead.tsx"),
        os.path.join("camera", "CameraCard.tsx"),
        os.path.join("camera", "CameraGrid.tsx"),
        os.path.join("camera", "PTZControls.tsx"),
        os.path.join("alerts", "AlertBadge.tsx"),
        os.path.join("alerts", "AlertList.tsx"),
        os.path.join("alerts", "AlertDetailModal.tsx"),
        os.path.join("incidents", "ExplainableAICard.tsx"),
        os.path.join("incidents", "IncidentTimeline.tsx"),
        os.path.join("video", "HUDOverlay.tsx"),
        os.path.join("video", "LiveStreamPlayer.tsx"),
        os.path.join("video", "EvidencePlayback.tsx"),
        os.path.join("maps", "TacticalMap.tsx"),
        os.path.join("charts", "ThreatRadarChart.tsx"),
        os.path.join("charts", "HourlyBreachChart.tsx"),
        os.path.join("charts", "RiskDistributionChart.tsx"),
    ]
    for comp in expected_components:
        comp_path = os.path.join(components_dir, comp)
        assert os.path.exists(comp_path), f"Component {comp} missing from {components_dir}"
        with open(comp_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 150, f"Component {comp} content is too short"

def test_frontend_aesthetic_and_strategic_copy_mandates():
    """Verify specific aesthetic and marketing directives requested by user."""
    # 1. Checkmark bullets (✓) and 3 tiers in PricingTiers.tsx
    pricing_path = os.path.join(FRONTEND_DIR, "src", "components", "common", "PricingTiers.tsx")
    with open(pricing_path, "r", encoding="utf-8") as f:
        pricing_code = f.read()
    assert "✓" in pricing_code, "Checkmark bullet (✓) missing from PricingTiers"
    assert "Tactical Post" in pricing_code
    assert "Sector HQ Battalion" in pricing_code
    assert "Sovereign Fleet Command" in pricing_code
    assert "RECOMMENDED STRATEGIC" in pricing_code

    # 2. Strategic "It's not X, it's Y" copy & em dashes (—)
    about_path = os.path.join(FRONTEND_DIR, "src", "pages", "About.tsx")
    with open(about_path, "r", encoding="utf-8") as f:
        about_code = f.read()
    assert "It's not" in about_code, "Strategic 'It\'s not X, it\'s Y' copy missing from About.tsx"
    assert "—" in about_code, "Em dash (—) missing from About.tsx"

    # 3. CTA button placed ABOVE input fields in CTASection.tsx
    cta_path = os.path.join(FRONTEND_DIR, "src", "components", "common", "CTASection.tsx")
    with open(cta_path, "r", encoding="utf-8") as f:
        cta_code = f.read()
    btn_index = cta_code.find("<button")
    input_index = cta_code.find("<input")
    assert btn_index != -1 and input_index != -1
    assert btn_index < input_index, "CTA button MUST be placed ABOVE input fields as mandated"

    # 4. Liquid glass and colored left stripes
    card_path = os.path.join(FRONTEND_DIR, "src", "components", "camera", "CameraCard.tsx")
    with open(card_path, "r", encoding="utf-8") as f:
        card_code = f.read()
    assert "liquid-glass" in card_code or "backdrop-blur" in card_code
    assert "border-l-4 border-emerald-500" in card_code
    assert "border-l-4 border-rose-500" in card_code

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
