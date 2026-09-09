"""
IBVAP - End-to-End Video Processing Script
Processes a video file through the complete AI pipeline and produces:
1. Annotated output video with bounding boxes
2. JSON event log
3. Performance report

Usage:
    python scripts/process_video.py --source sample.mp4 --camera CAM-01
    python scripts/process_video.py --source 0  (for webcam)
    python scripts/process_video.py --source rtsp://ip:port/stream --camera CAM-BOP-01
"""
import sys
import os
import json
import time
import argparse
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("ibvap.process_video")

import numpy as np

try:
    import cv2
except ImportError:
    print("ERROR: OpenCV is required. Install with: pip install opencv-python")
    sys.exit(1)


def draw_detections(frame, detections, frame_h, frame_w):
    """Draw bounding boxes and labels on frame."""
    colors = {
        "person": (0, 255, 0),     # Green
        "vehicle": (255, 165, 0),   # Orange
        "animal": (255, 255, 0),    # Yellow
    }
    default_color = (0, 200, 255)

    for det in detections:
        bbox = det.get("bbox", [])
        if len(bbox) != 4:
            continue
        x1 = int(bbox[0] * frame_w)
        y1 = int(bbox[1] * frame_h)
        x2 = int(bbox[2] * frame_w)
        y2 = int(bbox[3] * frame_h)

        class_name = det.get("class_name", "unknown")
        confidence = det.get("confidence", 0)
        color = colors.get(class_name, default_color)

        # Draw box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Draw label
        label = f"{class_name} {confidence:.2f}"
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - label_size[1] - 6), (x1 + label_size[0], y1), color, -1)
        cv2.putText(frame, label, (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    return frame


def draw_status_bar(frame, frame_num, fps, detections_count, risk_score, severity):
    """Draw a status bar at the top of the frame."""
    h, w = frame.shape[:2]
    bar_h = 32
    cv2.rectangle(frame, (0, 0), (w, bar_h), (20, 20, 20), -1)

    sev_colors = {
        "NORMAL": (0, 200, 0), "LOW": (0, 255, 255), "MEDIUM": (0, 165, 255),
        "HIGH": (0, 0, 255), "CRITICAL": (0, 0, 200),
    }
    sev_color = sev_colors.get(severity, (200, 200, 200))

    text = (
        f"IBVAP | Frame: {frame_num} | FPS: {fps:.1f} | "
        f"Detections: {detections_count} | Risk: {risk_score} [{severity}]"
    )
    cv2.putText(frame, text, (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, sev_color, 1)
    return frame


def main():
    parser = argparse.ArgumentParser(description="IBVAP End-to-End Video Processor")
    parser.add_argument("--source", required=True, help="Video file path, webcam ID (0), or RTSP URL")
    parser.add_argument("--camera", default="CAM-01", help="Camera ID for this source")
    parser.add_argument("--output", default=None, help="Output annotated video path")
    parser.add_argument("--max-frames", type=int, default=0, help="Max frames to process (0=all)")
    parser.add_argument("--show", action="store_true", help="Display live preview window")
    parser.add_argument("--fps", type=int, default=10, help="Analysis FPS (skip frames)")
    parser.add_argument("--confidence", type=float, default=0.25, help="Detection confidence threshold")
    args = parser.parse_args()

    # ── Initialize Detector ──
    logger.info("=" * 60)
    logger.info("IBVAP - Intelligent Border Video Analytics Platform")
    logger.info("=" * 60)

    from ai.detection.real_detector import RealDetector
    detector = RealDetector(confidence_threshold=args.confidence)

    if not detector.is_ready():
        logger.error("FATAL: Detection model failed to load. Cannot proceed.")
        sys.exit(1)

    health = detector.get_health()
    logger.info(f"Detector: {health['model_name']} on {health['device']}")
    logger.info(f"Confidence threshold: {args.confidence}")

    # ── Open Video Source ──
    from ai.stream.video_source import create_source
    source = create_source(args.source, source_id=args.camera)
    if not source.connect():
        logger.error(f"FATAL: Cannot open video source: {args.source}")
        sys.exit(1)

    source_stats = source.get_stats()
    logger.info(f"Source: {args.source} ({source_stats['source_fps']} FPS)")

    # ── Setup Output ──
    out_writer = None
    output_path = args.output
    events_log = []

    # ── Processing Loop ──
    frame_num = 0
    processed = 0
    source_fps = source.get_fps() or 25.0
    skip_interval = max(1, int(source_fps / args.fps))
    total_det_time = 0.0
    total_detections = 0

    logger.info(f"Processing at {args.fps} FPS (skip every {skip_interval} frames)")
    logger.info("-" * 60)

    try:
        while True:
            ret, frame = source.read()
            if not ret or frame is None:
                break

            frame_num += 1

            # Frame sampling — process every Nth frame
            if frame_num % skip_interval != 0:
                continue

            h, w = frame.shape[:2]
            processed += 1

            if args.max_frames > 0 and processed > args.max_frames:
                break

            # ── Run Detection ──
            t0 = time.perf_counter()
            detections = detector.detect(frame)
            det_ms = (time.perf_counter() - t0) * 1000.0
            total_det_time += det_ms
            total_detections += len(detections)

            det_dicts = [d.to_dict() for d in detections]

            # ── Calculate Risk ──
            persons = sum(1 for d in detections if d.class_name == "person")
            vehicles = sum(1 for d in detections if d.class_name == "vehicle")
            risk_score = 0
            severity = "NORMAL"
            if persons > 0:
                risk_score += 30
            if vehicles > 0:
                risk_score += 20
            if persons > 2:
                risk_score += 10
            if risk_score > 89:
                severity = "HIGH"
            elif risk_score > 59:
                severity = "MEDIUM"
            elif risk_score > 29:
                severity = "LOW"

            # ── Log Event ──
            if detections:
                event = {
                    "frame": frame_num,
                    "timestamp": time.time(),
                    "camera_id": args.camera,
                    "detections": len(detections),
                    "persons": persons,
                    "vehicles": vehicles,
                    "risk_score": risk_score,
                    "severity": severity,
                    "detection_ms": round(det_ms, 2),
                    "details": det_dicts,
                }
                events_log.append(event)

            # ── Draw Annotations ──
            annotated = draw_detections(frame.copy(), det_dicts, h, w)
            avg_fps = processed / (total_det_time / 1000.0) if total_det_time > 0 else 0
            annotated = draw_status_bar(annotated, frame_num, avg_fps, len(detections), risk_score, severity)

            # ── Setup Output Writer (on first frame) ──
            if out_writer is None and output_path:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out_writer = cv2.VideoWriter(output_path, fourcc, args.fps, (w, h))

            if out_writer:
                out_writer.write(annotated)

            # ── Live Preview ──
            if args.show:
                cv2.imshow("IBVAP Live", annotated)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("Preview closed by user")
                    break

            # ── Progress Logging ──
            if processed % 50 == 0:
                avg_det_ms = total_det_time / processed
                logger.info(
                    f"Frame {frame_num}: {len(detections)} detections | "
                    f"{det_ms:.1f}ms | avg {avg_det_ms:.1f}ms | "
                    f"P:{persons} V:{vehicles}"
                )

    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
    finally:
        source.release()
        if out_writer:
            out_writer.release()
        if args.show:
            cv2.destroyAllWindows()

    # ── Performance Report ──
    logger.info("=" * 60)
    logger.info("IBVAP Processing Complete")
    logger.info("=" * 60)
    avg_det_ms = total_det_time / processed if processed > 0 else 0
    avg_fps = 1000.0 / avg_det_ms if avg_det_ms > 0 else 0

    report = {
        "source": args.source,
        "camera_id": args.camera,
        "total_source_frames": frame_num,
        "frames_processed": processed,
        "total_detections": total_detections,
        "unique_events": len(events_log),
        "avg_detection_ms": round(avg_det_ms, 2),
        "avg_fps": round(avg_fps, 1),
        "detector": health,
    }

    logger.info(f"Frames processed:  {processed}")
    logger.info(f"Total detections:  {total_detections}")
    logger.info(f"Events logged:     {len(events_log)}")
    logger.info(f"Avg detection:     {avg_det_ms:.2f} ms")
    logger.info(f"Avg throughput:    {avg_fps:.1f} FPS")
    logger.info(f"Model:             {health['model_name']} on {health['device']}")

    # ── Save JSON Output ──
    json_path = output_path.replace(".mp4", "_events.json") if output_path else "ibvap_events.json"
    with open(json_path, "w") as f:
        json.dump({
            "report": report,
            "events": events_log,
        }, f, indent=2, default=str)
    logger.info(f"Events saved to:   {json_path}")

    if output_path:
        logger.info(f"Output video:      {output_path}")

    logger.info("=" * 60)


if __name__ == "__main__":
    main()
