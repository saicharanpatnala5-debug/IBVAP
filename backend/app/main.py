"""
IBVAP - Intelligent Border Video Analytics Platform
Main Application Factory & Lifespan Orchestrator
SIH 2026 | Problem Statement: SIH26187 (SSB / Ministry of Home Affairs)
"""
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import cv2
from ultralytics import YOLO
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging, logger
from app.api.websocket import ws_manager
from app.api.routes import (
    auth_router, cameras_router, zones_router, events_router, incidents_router,
    alerts_router, anpr_router, faces_router, search_router, health_router,
    audit_router, demo_router, streams_router, detections_router,
    tracks_router, vehicles_router, analytics_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    setup_logging()
    logger.info("Initializing IBVAP Backend System...")
    await init_db()
    logger.info("Database schema synchronized.")
    yield
    # Shutdown tasks
    logger.info("Shutting down IBVAP Backend System...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Software-Defined AI Video Intelligence Platform transforming existing CCTV infrastructure into smart border surveillance.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve stored evidence frames & clips statically
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
app.mount("/storage", StaticFiles(directory=settings.STORAGE_DIR), name="storage")

# Serve static dashboard assets, sample videos & processed forensic inference outputs
os.makedirs("static", exist_ok=True)
os.makedirs("static/detect", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
VIDEOS_DIR = os.path.join(STATIC_DIR, "videos")
if os.path.exists(VIDEOS_DIR):
    app.mount("/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")

# Mount API routes
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(cameras_router, prefix=settings.API_V1_STR)
app.include_router(zones_router, prefix=settings.API_V1_STR)
app.include_router(events_router, prefix=settings.API_V1_STR)
app.include_router(incidents_router, prefix=settings.API_V1_STR)
app.include_router(alerts_router, prefix=settings.API_V1_STR)
app.include_router(anpr_router, prefix=settings.API_V1_STR)
app.include_router(faces_router, prefix=settings.API_V1_STR)
app.include_router(search_router, prefix=settings.API_V1_STR)
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)
app.include_router(streams_router, prefix=settings.API_V1_STR)
app.include_router(detections_router, prefix=settings.API_V1_STR)
app.include_router(tracks_router, prefix=settings.API_V1_STR)
app.include_router(vehicles_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)

# Top-level direct streaming endpoints (for instant access by frontend img tags)
import cv2
import time
from ultralytics import YOLO
from fastapi.responses import StreamingResponse
from typing import Optional

# Initialize YOLO model
model = YOLO("yolov8n.pt")
yolo_model = model

@app.post("/api/analyze_video")
async def analyze_video(file: UploadFile = File(...)):
    os.makedirs("static", exist_ok=True)
    os.makedirs("static/detect", exist_ok=True)
    input_path = f"static/input_{file.filename}"
    output_path = f"static/annotated_{file.filename}"
    
    with open(input_path, "wb") as f:
        f.write(await file.read())
        
    # Run YOLO inference and save processed video
    results = model.predict(source=input_path, save=True, conf=0.25, project="static", name="detect", exist_ok=True)
    
    # Extract real stats for HUD
    detected_classes = set()
    for r in results:
        for c in r.boxes.cls:
            detected_classes.add(model.names[int(c)])
            
    # Ensure processed video is browser-playable MP4 at static/detect/input_{file.filename}
    target_path = os.path.abspath(f"static/detect/input_{file.filename}")
    if results and hasattr(results[0], "save_dir"):
        save_dir = results[0].save_dir
        if os.path.exists(save_dir):
            base_prefix = f"input_{os.path.splitext(file.filename)[0]}"
            saved_file = None
            for fname in os.listdir(save_dir):
                if fname.startswith(base_prefix):
                    saved_file = os.path.join(save_dir, fname)
                    break
            if saved_file and os.path.exists(saved_file):
                try:
                    import imageio_ffmpeg, subprocess
                    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                    subprocess.run(
                        [ffmpeg_exe, "-y", "-i", saved_file, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast", target_path],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
                    )
                except Exception:
                    import shutil
                    shutil.copy(saved_file, target_path)

    # In case conversion was bypassed or target doesn't exist, ensure fallback
    if not os.path.exists(target_path):
        import shutil
        if os.path.exists(input_path):
            shutil.copy(input_path, target_path)

    # Format high-confidence detections for HUD and overlay
    VEHICLE_CLASSES = {"car", "truck", "bus", "motorcycle", "bicycle", "boat", "train"}
    ANIMAL_CLASSES = {"dog", "cat", "bird", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe"}
    
    unique_detections = []
    seen_classes = set()
    track_counter = 1
    
    for r in results:
        h, w = r.orig_shape[:2]
        for b in r.boxes:
            cls_id = int(b.cls[0])
            conf = float(b.conf[0])
            raw_name = r.names[cls_id].lower()
            
            if raw_name == "person":
                class_name = "person"
                threat_level = "CRITICAL"
                color = "#f43f5e"
                cls_code = "P"
                label = f"TARGET: PERSON ({int(conf*100)}%)"
            elif raw_name in VEHICLE_CLASSES:
                class_name = "vehicle"
                is_heavy = raw_name in {"truck", "bus", "train"}
                threat_level = "HIGH" if is_heavy else "MODERATE"
                color = "#06b6d4"
                cls_code = "HV" if is_heavy else "V"
                label = f"TARGET: {raw_name.upper()} ({int(conf*100)}%)"
            elif raw_name in ANIMAL_CLASSES:
                class_name = "animal"
                threat_level = "LOW"
                color = "#f59e0b"
                cls_code = "A"
                label = f"FAUNA: {raw_name.upper()} (FILTERED)"
            else:
                class_name = "object"
                threat_level = "MODERATE"
                color = "#a855f7"
                cls_code = "OBJ"
                label = f"OBJECT: {raw_name.upper()}"
                
            xyxy = b.xyxy[0].tolist()
            bx = max(0.0, xyxy[0] / float(w))
            by = max(0.0, xyxy[1] / float(h))
            bw = min(1.0, (xyxy[2] - xyxy[0]) / float(w))
            bh = min(1.0, (xyxy[3] - xyxy[1]) / float(h))
            
            key = (class_name, round(bx, 1), round(by, 1))
            if key not in seen_classes and len(unique_detections) < 15:
                seen_classes.add(key)
                track_id = f"TRK-{cls_code}{100 + track_counter}"
                track_counter += 1

                anpr_read = None
                sub_label = f"{raw_name.upper()} (YOLOv8 {int(conf*100)}%)"

                if raw_name in VEHICLE_CLASSES:
                    vx1 = max(0, min(w - 1, int(xyxy[0])))
                    vy1 = max(0, min(h - 1, int(xyxy[1])))
                    vx2 = max(0, min(w, int(xyxy[2])))
                    vy2 = max(0, min(h, int(xyxy[3])))
                    if (vx2 - vx1) > 25 and (vy2 - vy1) > 25:
                        orig_frame = getattr(r, 'orig_img', None)
                        if orig_frame is not None:
                            vehicle_crop = orig_frame[vy1:vy2, vx1:vx2]
                            try:
                                from app.ai.anpr_engine import anpr_engine
                                anpr_read = anpr_engine.detect_and_recognize_vehicle_plate(
                                    vehicle_crop=vehicle_crop,
                                    vehicle_class=raw_name,
                                    track_id=track_id
                                )
                                if anpr_read and anpr_read.get("plate_text"):
                                    p_text = anpr_read["plate_text"]
                                    c_pct = anpr_read.get("confidence_percentage", "")
                                    if anpr_read.get("requires_human_verification"):
                                        sub_label = f"PLATE: {p_text} ({c_pct}) [UNVERIFIED]"
                                    else:
                                        sub_label = f"PLATE: {p_text} ({c_pct}) [VERIFIED]"
                            except Exception:
                                pass

                unique_detections.append({
                    "id": f"CAM-01-{track_id.lower()}",
                    "track_id": track_id,
                    "class_name": class_name,
                    "label": label,
                    "sub_label": sub_label,
                    "confidence": round(conf, 3),
                    "bbox": [round(bx, 4), round(by, 4), round(bw, 4), round(bh, 4)],
                    "threat_level": threat_level,
                    "color": color,
                    "details": {
                        "yolo_class": raw_name,
                        "confidence_percentage": f"{int(conf*100)}%",
                        "is_filtered_false_alarm": class_name == "animal",
                        "anpr_plate": anpr_read["plate_text"] if anpr_read else None,
                        "anpr_norm": anpr_read["plate_norm"] if anpr_read else None,
                        "plate_bbox": anpr_read["plate_bbox"] if anpr_read else None,
                        "ocr_confidence": anpr_read["ocr_confidence"] if anpr_read else None,
                        "confidence_percentage_ocr": anpr_read["confidence_percentage"] if anpr_read else None,
                        "verification_status": anpr_read["verification_status"] if anpr_read else None,
                        "requires_human_verification": anpr_read.get("requires_human_verification", False) if anpr_read else False,
                        "plate_crop_b64": anpr_read.get("plate_crop_b64") if anpr_read else None,
                        "jurisdiction": anpr_read.get("jurisdiction") if anpr_read else None
                    }
                })

    anpr_results = []
    for d in unique_detections:
        det_anpr = d.get("details", {})
        if det_anpr.get("anpr_plate"):
            anpr_results.append({
                "track_id": d["track_id"],
                "plate_text": det_anpr["anpr_plate"],
                "plate_norm": det_anpr["anpr_norm"],
                "confidence": det_anpr["ocr_confidence"],
                "confidence_percentage": det_anpr["confidence_percentage_ocr"],
                "verification_status": det_anpr["verification_status"],
                "requires_human_verification": det_anpr["requires_human_verification"],
                "bbox": det_anpr["plate_bbox"],
                "vehicle_class": det_anpr.get("yolo_class", "vehicle"),
                "vehicle_bbox": d["bbox"],
                "plate_crop_b64": det_anpr.get("plate_crop_b64"),
                "jurisdiction": det_anpr.get("jurisdiction")
            })

    total_count = len(unique_detections)
    risk_score = 0
    if total_count > 0:
        risk_score = 95 if "person" in detected_classes else (55 if "vehicle" in detected_classes else 20)

    return {
        "status": "success",
        "processed_video_url": f"http://127.0.0.1:8000/static/detect/input_{file.filename}",
        "detected_classes": list(detected_classes),
        "risk_score": risk_score,
        "detections": unique_detections,
        "anpr_results": anpr_results,
        "person_count": sum(1 for d in unique_detections if d["class_name"] == "person"),
        "vehicle_count": sum(1 for d in unique_detections if d["class_name"] == "vehicle"),
        "object_count": sum(1 for d in unique_detections if d["class_name"] == "object"),
        "animal_count": sum(1 for d in unique_detections if d["class_name"] == "animal")
    }

def generate_yolo_stream(video_path: Optional[str] = None):
    # Determine video source using unified resolver
    from app.api.routes.detections import resolve_video_source
    video_source = resolve_video_source(video_path)

    if not video_source:
        if not video_path:
            default_candidates = [
                os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "videos", "traffic_anpr_delhi_4k.mp4")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "videos", "scenario_01_perimeter_breach.mp4")),
                os.path.abspath(os.path.join(os.getcwd(), "backend", "app", "static", "videos", "scenario_01_perimeter_breach.mp4")),
            ]
            for dc in default_candidates:
                if os.path.isfile(dc):
                    video_source = dc
                    break
        else:
            logger.warning(f"Requested video_path '{video_path}' could not be resolved.")

    cap = cv2.VideoCapture(video_source if video_source else 0)

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.05)
                    continue

            # Run YOLO inference
            if yolo_model:
                results = yolo_model(frame, verbose=False)
                # Draws the bounding boxes on the frame using the YOLO results
                annotated_frame = results[0].plot()
            else:
                annotated_frame = frame

            # Encode the frame: _, buffer = cv2.imencode('.jpg', frame)
            _, buffer = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            frame_bytes = buffer.tobytes()

            # Yield the byte stream using multipart/x-mixed-replace; boundary=frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.033)
    finally:
        cap.release()

@app.get("/api/video_feed")
def video_feed(video_path: Optional[str] = None):
    """FastAPI YOLO Inference Video Stream endpoint returning multipart/x-mixed-replace JPEG stream."""
    return StreamingResponse(
        generate_yolo_stream(video_path=video_path),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/api/stats")
def top_level_stats():
    """Direct top-level telemetry endpoint returning active detection counts and risk score."""
    from app.api.routes.detections import get_stream_stats
    return get_stream_stats()

# Real-Time WebSockets for Alerts & Telemetry
@app.websocket("/ws/alerts")
@app.websocket("/ws/telemetry")
async def websocket_alerts_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep-alive receive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

@app.get("/dashboard", include_in_schema=False)
@app.get("/ui", include_in_schema=False)
@app.get("/live", include_in_schema=False)
@app.get("/cameras", include_in_schema=False)
@app.get("/alerts", include_in_schema=False)
@app.get("/incidents", include_in_schema=False)
@app.get("/incident-details", include_in_schema=False)
@app.get("/search", include_in_schema=False)
@app.get("/analytics", include_in_schema=False)
@app.get("/map", include_in_schema=False)
@app.get("/settings", include_in_schema=False)
@app.get("/upload", include_in_schema=False)
async def serve_dashboard():
    static_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return {"status": "Frontend dashboard static file not found"}

@app.get("/", include_in_schema=False)
async def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        static_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
        if os.path.exists(static_file):
            return FileResponse(static_file)
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "documentation": "/docs",
        "api_v1": settings.API_V1_STR,
        "sih_scenario_endpoint": "/api/demo/run-scenario"
    }
