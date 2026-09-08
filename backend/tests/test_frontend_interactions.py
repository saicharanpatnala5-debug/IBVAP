import os
import re
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FRONTEND_HTML = os.path.join(PROJECT_ROOT, "frontend", "public", "index.html")

def test_all_sidebar_tabs_exist_in_dom():
    """Ensure every switchTab call in index.html matches an existing tab-id in the DOM."""
    with open(FRONTEND_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    calls = re.findall(r"switchTab\(['\"]([^'\"]+)['\"]\)", html)
    assert len(calls) >= 13, f"Expected at least 13 tab references, found {len(calls)}"

    unique_tabs = set(calls)
    for tab in unique_tabs:
        expected_id = f'id="tab-{tab}"'
        assert expected_id in html, f"Target tab container {expected_id} missing from HTML DOM!"

def test_all_interactive_functions_defined():
    """Ensure every interactive function called by UI buttons is properly declared in script."""
    with open(FRONTEND_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    expected_functions = [
        "switchTab",
        "playTacticalSound",
        "showToast",
        "cycleDefcon",
        "cycleUserRole",
        "toggleAudio",
        "toggleThermalMode",
        "triggerSnapshot",
        "toggleRecord",
        "triggerPTZ",
        "setLiveLayout",
        "triggerQRT",
        "lockdownSector",
        "rebootNode",
        "rebootAllCameras",
        "acknowledgeAlert",
        "acknowledgeAllAlerts",
        "filterAlerts",
        "searchAlerts",
        "exportAlertsCSV",
        "verifyShaLedger",
        "signAndSealDossier",
        "runForensicSearch",
        "applySearchPreset",
        "clearSearchQuery",
        "setAnalyticsWindow",
        "toggleMapLayer",
        "saveAndSyncWeights",
        "resetSettingsDefaults",
        "requestTierQuote",
        "submitDeploymentDossier",
        "submitDispatchBrief",
        "downloadPgpKey",
    ]

    for fn in expected_functions:
        pattern = f"function {fn}("
        assert pattern in html, f"Function {fn} missing from HTML javascript block!"

def test_aesthetic_and_strategic_elements_in_html():
    """Verify mandated styling classes, copy, and structural markers."""
    with open(FRONTEND_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    assert "liquid-glass" in html
    assert "reticle-grid" in html
    assert "stream-canvas" in html
    assert "It's not passive CCTV monitoring — it's proactive autonomous border dominance." in html
    assert "✓" in html
    assert "RECOMMENDED STRATEGIC" in html
    assert "defcon-badge" in html
    assert "user-display-role" in html
    assert "header-alert-count" in html

def test_cctv_upload_lab_subsystem():
    """Verify CCTV Footage Upload Lab elements, file inputs, video player, and handlers."""
    with open(FRONTEND_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # Upload Tab container and inputs
    assert 'id="tab-upload"' in html
    assert 'id="cctv-file-input"' in html
    assert 'id="cctv-dropzone"' in html
    assert 'id="uploaded-cctv-video"' in html
    assert 'id="uploaded-cctv-canvas"' in html
    assert 'id="loaded-video-title"' in html

    # Functions defined
    for fn in ["openCctvUpload", "handleCctvFileUpload", "loadSampleCctvVideo", "toggleVideoPlayPause", "stepVideoFrame", "setVideoSpeed", "toggleVideoDetectionOverlay", "exportVideoForensicReport", "clearCctvVideo"]:
        assert f"function {fn}(" in html, f"CCTV Upload function {fn} missing from HTML script!"

    # Tactical sample scenarios
    assert "scenario_01_perimeter_breach.mp4" in html
    assert "scenario_02_night_thermal_patrol.mp4" in html
    assert "scenario_03_checkpoint_anpr.mp4" in html
    assert "scenario_04_multicam_handoff.mp4" in html

def test_direct_live_cctv_linker_subsystem():
    """Verify Direct Live CCTV Connector modal, RTSP/HLS inputs, and WebCam integration."""
    with open(FRONTEND_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # Modal container and stream inputs
    assert 'id="live-cctv-modal"' in html
    assert 'id="custom-stream-url"' in html
    assert 'id="modal-tab-rtsp"' in html
    assert 'id="modal-tab-webcam"' in html
    assert 'id="modal-tab-fleet"' in html

    # Functions defined
    for fn in ["openLiveCctvModal", "closeLiveCctvModal", "switchModalTab", "connectDirectLiveStream", "connectLocalWebcam", "disconnectWebcam", "selectDirectFleetCam"]:
        assert f"function {fn}(" in html, f"Direct Live CCTV function {fn} missing from HTML script!"

    # WebCam / RTSP connection capabilities
    assert "navigator.mediaDevices.getUserMedia" in html
    assert "rtsp://" in html
    assert "YOLO26" in html


def test_sentinel_authentication_and_session_management():
    """Verify Sentinel Authentication Gateway, dynamic operator profiles, and session security."""
    with open(FRONTEND_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Login modal and operator form elements
    assert 'id="sentinel-login-modal"' in html, "Missing sentinel login gateway modal"
    assert 'id="login-input-name"' in html, "Missing login operator name input"
    assert 'id="login-input-id"' in html, "Missing login service ID input"
    assert 'id="login-input-role"' in html, "Missing login role select"
    assert 'id="login-input-key"' in html, "Missing login passcode input"
    assert 'id="btn-login-submit"' in html, "Missing login submit button"

    # 2. Verified 1-click presets
    assert "Sai Charan" in html, "Sai Charan preset missing"
    assert "CMD-001-SC" in html, "Lead service ID missing"

    # 3. Dynamic header profile and session telemetry
    assert 'id="operator-profile-btn"' in html, "Missing operator profile header button"
    assert 'id="operator-dropdown-menu"' in html, "Missing operator dropdown menu"
    assert 'id="user-display-name"' in html, "Missing dynamic user display name"
    assert 'id="user-display-role"' in html, "Missing dynamic user display role"
    assert 'id="session-uptime-display"' in html, "Missing session uptime telemetry"
    assert 'id="report-signer"' in html, "Missing dynamic FIR report signer"

    # 4. Core auth and session functions
    expected_auth_fns = [
        "checkAuth",
        "showLoginModal",
        "hideLoginModal",
        "selectLoginPreset",
        "handleLoginSubmit",
        "executeLogin",
        "applySessionToUI",
        "setOperatorRole",
        "toggleOperatorDropdown",
        "logoutOperator",
        "updateSessionUptime",
        "cycleUserRole"
    ]
    for fn in expected_auth_fns:
        assert f"function {fn}(" in html, f"Authentication function {fn} missing from HTML script!"

    # 5. LocalStorage session persistence
    assert "ibvap_session" in html, "ibvap_session localStorage key missing"

    # 6. Absence of stale unknown profile hardcodings
    assert "Commandant R. K. Verma" not in html, "Found stale hardcoded Commandant Verma profile!"


def test_anpr_number_plate_detection_and_vehicle_dossier():
    """Verify ANPR Number Plate localization, vehicle dossier modal, and canvas interactions."""
    with open(FRONTEND_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Vehicle Dossier Modal elements
    assert 'id="vehicle-dossier-modal"' in html, "Missing vehicle dossier modal"
    assert 'id="dossier-plate-number"' in html, "Missing dossier plate number"
    assert 'id="dossier-owner-name"' in html, "Missing dossier owner name"
    assert 'id="dossier-vehicle-model"' in html, "Missing dossier vehicle model"
    assert 'id="dossier-hsrp-laser"' in html, "Missing dossier HSRP laser code"

    # 2. Sidebar Live ANPR Card
    assert 'id="sidebar-plate-display"' in html, "Missing sidebar plate display"
    assert "DL 01 AB 1234" in html, "Missing plate text DL 01 AB 1234"

    # 3. Canvas pointer events enabled
    assert 'pointer-events-auto cursor-crosshair' in html, "CCTV canvas must have pointer-events-auto"

    # 4. ANPR functions
    expected_anpr_fns = [
        "quickLoginSaiCharan",
        "openVehicleDossier",
        "closeVehicleDossier",
        "whitelistCurrentVehicle",
        "flagBoloCurrentVehicle",
        "exportVehicleDossierReport",
        "setupCanvasInteractions"
    ]
    for fn in expected_anpr_fns:
        assert f"function {fn}(" in html, f"ANPR function {fn} missing from HTML script!"

    # 5. ANPR Number Plate localization in perception engine
    assert "ANPR NUMBER PLATE LOCALIZATION" in html, "Perception engine missing ANPR number plate localization"


