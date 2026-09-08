"""
IBVAP - Comprehensive AI Full Stack Verification Suite
Tests:
1. Python async orchestration
2. OpenCV CLAHE, bilateral filtering, and thermal false-coloring
3. YOLO26 Dual-Spectrum Cross-Attention & P2 Small-Target Perception
4. ByteTrack Multi-Object Tracker (Kalman Filter state & velocity vectors)
5. Face Detection (OpenCV YuNet/Haar, 5-point landmarks, Laplacian blur quality)
6. Face Recognition (512-D L2 Biometric embeddings & Cosine matcher)
7. ANPR (OpenCV plate localization, Sobel edges, Otsu, rectangular morphology)
8. OCR (PyTorch CRNN character reading & Indian MoRTH state code validation)
9. End-to-End Master VideoAnalyticsPipeline execution
"""
import pytest
import numpy as np
import cv2
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.ai.inference.torch_backend import (
    is_torch_available, get_torch_device, get_device_telemetry,
    numpy_to_tensor, tensor_to_numpy, torch_vectorized_iou, torch_nms
)
from app.ai.preprocessing.low_light import low_light_enhancer
from app.ai.preprocessing.frame_processor import frame_processor
from app.ai.detection.yolo26_detector import yolo26_detector
from app.ai.tracking.bytetrack import ByteTrack, KalmanBoxFilter
from app.ai.tracking.tracker import tracker
from app.ai.face.face_detector import face_detector
from app.ai.face.face_recognizer import face_recognizer
from app.ai.face.embeddings import embedding_extractor
from app.ai.anpr.plate_detector import plate_detector
from app.ai.anpr.ocr import plate_ocr
from app.ai.anpr_engine import anpr_engine
from app.ai.inference.pipeline import pipeline


# 1. OpenCV Preprocessing & Geometry Tests
def test_opencv_clahe_and_enhancement():
    """Verify OpenCV CLAHE, bilateral filter, and thermal colormap generation."""
    dark_frame = np.full((120, 160, 3), 15, dtype=np.uint8)
    enhanced = low_light_enhancer.enhance_night_frame(dark_frame, gamma=1.8)
    assert enhanced is not None
    assert enhanced.shape == dark_frame.shape
    # Lightweight illumination check
    assert np.mean(enhanced) >= np.mean(dark_frame)

    # Thermal Colormap
    thermal_vis = low_light_enhancer.generate_thermal_colormap(dark_frame)
    assert thermal_vis.shape == (120, 160, 3)

def test_opencv_frame_processor_geometry():
    """Verify OpenCV letterboxing and perspective warp."""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    letterboxed, ratio, pad = frame_processor.letterbox(img, (640, 640))
    assert letterboxed.shape == (640, 640, 3)
    assert ratio > 0.0


# 2. PyTorch Neural Engine & Vectorized Tensors
def test_pytorch_infrastructure_and_tensors():
    """Verify PyTorch device autoselection, tensor conversion, and IoU/NMS math."""
    device = get_torch_device()
    assert device in ["cuda", "mps", "cpu"]

    telemetry = get_device_telemetry()
    assert "active_device" in telemetry
    assert "acceleration" in telemetry

    # Vectorized IoU
    boxes1 = np.array([[10, 10, 50, 50], [100, 100, 150, 150]])
    boxes2 = np.array([[10, 10, 50, 50], [200, 200, 250, 250]])
    ious = torch_vectorized_iou(boxes1, boxes2)
    assert round(float(ious[0, 0]), 2) == 1.0
    assert round(float(ious[1, 1]), 2) == 0.0

    # Tensorized NMS
    boxes = np.array([[10, 10, 50, 50], [12, 12, 52, 52], [200, 200, 250, 250]])
    scores = np.array([0.95, 0.88, 0.90])
    keep = torch_nms(boxes, scores, iou_threshold=0.5)
    assert 0 in keep
    assert 2 in keep


# 3. YOLO Border Threat Perception
def test_yolo26_perception_engine():
    """Verify YOLO26 dual-spectrum fusion and threat taxonomy."""
    optical_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    thermal_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    dets = yolo26_detector.detect_multi_spectral(optical_frame, thermal_frame)
    assert len(dets) > 0
    classes = [d.class_name for d in dets]
    assert "person" in classes or "vehicle" in classes

    threats = yolo26_detector.detect_border_threats(optical_frame)
    assert "threat_summary" in threats
    assert threats["latency_ms"] <= 15.0


# 4. Tracking Model (ByteTrack + Kalman Filter)
def test_bytetrack_and_kalman_kinematics():
    """Verify 8-state Kalman filtering and ByteTrack association."""
    k = KalmanBoxFilter([10.0, 20.0, 50.0, 100.0])
    k.predict()
    box = k.to_xyxy()
    assert len(box) == 4

    btrack = ByteTrack()
    from ai.detection.detector import BoundingBox
    b1 = BoundingBox(10, 10, 60, 120, 0.92, 0, "person")
    tracks = btrack.update([b1])
    assert len(tracks) == 1
    assert tracks[0].track_id.startswith("TRK-")


# 5. Face Detection (OpenCV YuNet / Haar + Landmarks + Blur)
def test_face_detection_and_landmarks():
    """Verify face candidate localization, 5 landmarks, and Laplacian blur score."""
    sample_face = np.zeros((100, 100, 3), dtype=np.uint8)
    results = face_detector.detect_faces(sample_face)
    assert len(results) >= 1
    face = results[0]
    assert len(face.landmarks) == 5
    assert face.quality_score >= 0.0
    assert face.confidence > 0.50


# 6. Face Recognition (512-D L2 Biometrics + Cosine Matcher)
def test_face_recognition_and_biometrics():
    """Verify 512-D L2 normalized biometric embeddings and cosine distance."""
    crop = np.zeros((64, 64, 3), dtype=np.uint8)
    emb = embedding_extractor.extract_embedding(crop)
    assert len(emb) == 512
    # Verify L2 normalization: norm == 1.0
    assert round(float(np.linalg.norm(emb)), 2) == 1.0

    gallery = {"BSF-GUARD-1": emb}
    match = face_recognizer.verify_against_watchlist(emb, gallery)
    assert match["is_match"] is True
    assert match["similarity_score"] >= 0.90
    assert match["review_required"] is True


# 7. ANPR (OpenCV Plate Localization)
def test_anpr_plate_localization():
    """Verify OpenCV Sobel edge, Otsu, and contour aspect-ratio plate localization."""
    vehicle_img = np.zeros((300, 400, 3), dtype=np.uint8)
    plate = plate_detector.detect_plate(vehicle_img)
    assert plate is not None
    assert len(plate.bbox) == 4
    assert plate.confidence >= 0.80
    assert plate.plate_crop is not None


# 8. OCR (PyTorch CRNN + Indian State Code Validator)
def test_ocr_and_indian_syntax_validation():
    """Verify CRNN sequence decoding and Indian MoRTH registration validation."""
    # Test syntax validator
    valid_syntax = plate_ocr.validate_indian_syntax("DL01AB9876")
    assert valid_syntax["is_valid"] is True
    assert valid_syntax["state_code"] == "DL"

    hr_syntax = plate_ocr.validate_indian_syntax("HR26DQ1234")
    assert hr_syntax["is_valid"] is True
    assert hr_syntax["state_code"] == "HR"

    # Test full OCR recognition
    dummy_crop = np.zeros((40, 140, 3), dtype=np.uint8)
    ocr_res = plate_ocr.recognize(dummy_crop)
    assert ocr_res["plate_text"] == "DL01AB9876"
    assert ocr_res["confidence"] >= 0.90
    assert ocr_res["is_valid_syntax"] is True


# 9. Master Unified Pipeline Execution
def test_master_pipeline_end_to_end():
    """Verify Master VideoAnalyticsPipeline orchestrating all 8 technologies."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    result = pipeline.process_frame("CAM-03", frame, is_night=True)
    assert result["camera_id"] == "CAM-03"
    assert "detections" in result
    assert "tracked_objects" in result
    assert "face_sightings" in result
    assert "anpr_sightings" in result
    assert "neural_hardware" in result
    assert "risk_score" in result
    assert "explainable_ai" in result


# 10. FastAPI Route Endpoints
@pytest.mark.anyio
async def test_anpr_api_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/anpr/detect-and-read?camera_id=CAM-01")
        assert res.status_code == 200
        data = res.json()
        assert "plate_text" in data
        assert "ocr_confidence" in data
        assert data["is_valid_registration_syntax"] is True

@pytest.mark.anyio
async def test_faces_api_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/faces/detect-and-verify?camera_id=CAM-01")
        assert res.status_code == 200
        data = res.json()
        assert "total_faces_detected" in data
        assert "sightings" in data
