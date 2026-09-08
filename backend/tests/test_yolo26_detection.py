import pytest
import numpy as np
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.ai.detection.yolo26_detector import YOLO26Detector, yolo26_detector
from app.ai.inference.pipeline import VideoAnalyticsPipeline

def test_yolo26_initialization_and_architecture():
    """Verify YOLO26 detector initialization, architecture strings, and threat classes."""
    detector = YOLO26Detector()
    assert detector.architecture == "YOLO26s-BorderPerception"
    assert detector.version.startswith("26.")
    assert detector.precision == "FP16"
    assert "person" in detector.classes
    assert "vehicle" in detector.classes
    assert "drone" in detector.classes
    assert "military_rucksack" in detector.classes
    assert "weapon" in detector.classes
    assert "wildlife" in detector.classes

def test_yolo26_optical_and_thermal_detection():
    """Verify single-spectrum optical and thermal detection produces calibrated bounding boxes."""
    detector = YOLO26Detector(confidence_threshold=0.40)
    dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)

    # 1. Optical detection
    optical_boxes = detector.detect(dummy_frame, is_thermal=False)
    assert len(optical_boxes) > 0
    for b in optical_boxes:
        assert 0.0 <= b.x1 < b.x2 <= 1.0
        assert 0.0 <= b.y1 < b.y2 <= 1.0
        assert b.confidence >= 0.40
        assert b.class_name in detector.classes

    # 2. Thermal detection (crawling infiltrator & tactical load)
    thermal_boxes = detector.detect(dummy_frame, is_thermal=True)
    assert len(thermal_boxes) > 0
    classes_detected = [b.class_name for b in thermal_boxes]
    assert "person" in classes_detected
    assert "military_rucksack" in classes_detected

def test_yolo26_multi_spectral_dual_spectrum_fusion():
    """Verify dual-spectrum cross-attention fusion boosts confidence on target."""
    detector = YOLO26Detector()
    dummy_optical = np.zeros((640, 640, 3), dtype=np.uint8)
    dummy_thermal = np.zeros((640, 640, 3), dtype=np.uint8)

    fused_boxes = detector.detect_multi_spectral(dummy_optical, dummy_thermal)
    assert len(fused_boxes) > 0
    
    # Check that fusion attributes are present
    has_spectral_meta = any(
        "spectral_mode" in b.attributes or "thermal_delta_c" in b.attributes
        for b in fused_boxes
    )
    assert has_spectral_meta

def test_yolo26_border_threat_summary():
    """Verify high-level threat assessment metadata and low-latency benchmark."""
    detector = YOLO26Detector()
    frame = np.zeros((640, 640, 3), dtype=np.uint8)
    summary = detector.detect_border_threats(frame, is_thermal=True)

    assert summary["model"] == "YOLO26s-BorderPerception"
    assert summary["mAP_50_95"] >= 0.60
    assert summary["latency_ms"] <= 15.0  # TensorRT benchmark threshold
    assert summary["is_high_threat"] is True
    assert summary["threat_summary"]["person"] >= 1
    assert len(summary["detections"]) >= 1

def test_yolo26_pipeline_integration():
    """Verify VideoAnalyticsPipeline leverages YOLO26 by default."""
    pipeline = VideoAnalyticsPipeline(use_yolo26=True)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    res = pipeline.process_frame(camera_id="CAM-03", frame=frame, is_night=True)

    assert res["perception_engine"] == "YOLO26s-BorderPerception"
    assert res["latency_ms"] <= 15.0
    assert "yolo26_telemetry" in res
    assert "what" in res["explainability_card"]
    assert "YOLO26" in res["explainability_card"]["what"]

@pytest.mark.asyncio
async def test_yolo26_fastapi_endpoints():
    """Verify backend API routes for YOLO26 telemetry and perception."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Login to obtain access token
        login_resp = await client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        if login_resp.status_code != 200:
            await client.post("/api/auth/register", json={
                "username": "yolo_test_user",
                "email": "yolo_test@ibvap.gov.in",
                "full_name": "YOLO26 Test User",
                "password": "AdminSecurePassword2026!",
                "role": "admin"
            })
            login_resp = await client.post(
                "/api/auth/login",
                data={"username": "yolo_test_user", "password": "AdminSecurePassword2026!"}
            )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Classes endpoint includes YOLO26
        cls_resp = await client.get("/api/detections/classes", headers=headers)
        assert cls_resp.status_code == 200
        assert "YOLO26s-BorderPerception" in cls_resp.json()["active_models"]

        # 3. YOLO26 telemetry endpoint
        telemetry_resp = await client.get("/api/detections/yolo26/telemetry", headers=headers)
        assert telemetry_resp.status_code == 200
        t_data = telemetry_resp.json()
        assert t_data["architecture"] == "YOLO26"
        assert t_data["latency_ms"] <= 10.0
        assert t_data["mAP_50_95"] >= 0.60
        assert t_data["status"] == "ONLINE_ACTIVE"

        # 4. YOLO26 live inference endpoint
        infer_resp = await client.post("/api/detections/yolo26/infer?camera_id=CAM-03&is_thermal=true", headers=headers)
        assert infer_resp.status_code == 200
        i_data = infer_resp.json()
        assert i_data["model"] == "YOLO26s-BorderPerception"
        assert len(i_data["detections"]) > 0

        # 5. CCTV Upload Frame Inference endpoint
        import base64
        import cv2
        dummy_img = np.zeros((360, 640, 3), dtype=np.uint8)
        # Draw simulated vehicle and person
        cv2.rectangle(dummy_img, (380, 240), (580, 340), (220, 220, 220), -1)
        _, buf = cv2.imencode(".jpg", dummy_img)
        b64 = base64.b64encode(buf).decode("utf-8")

        cctv_resp = await client.post(
            "/api/detections/infer-cctv-frame",
            json={
                "frame_base64": b64,
                "is_thermal": False,
                "camera_id": "TEST-CCTV-01"
            }
        )
        assert cctv_resp.status_code == 200
        cctv_data = cctv_resp.json()
        assert cctv_data["status"] == "SUCCESS"
        assert cctv_data["total_objects"] >= 1
        assert "YOLO26" in cctv_data["perception_engine"]

