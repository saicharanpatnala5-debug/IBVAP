"""
IBVAP - Evidence Capture and Snapshot Generator
Captures and persists evidence frames and clips for auditability and incident review.
"""
import os
from datetime import datetime, timezone
import uuid
from PIL import Image, ImageDraw, ImageFont
from app.core.config import settings

class EvidenceCaptureService:
    def __init__(self):
        self.snapshots_dir = settings.SNAPSHOTS_DIR
        self.clips_dir = settings.CLIPS_DIR
        os.makedirs(self.snapshots_dir, exist_ok=True)
        os.makedirs(self.clips_dir, exist_ok=True)

    def generate_evidence_frame(
        self,
        camera_id: str,
        event_title: str,
        bbox: list = None,
        plate_text: str = None
    ) -> str:
        """
        Creates a synthetic or annotated evidence image with military/tactical HUD styling.
        Returns the relative URL path to the saved image.
        """
        filename = f"ev_{camera_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.jpg"
        filepath = os.path.join(self.snapshots_dir, filename)

        # Create dark night-vision tactical surveillance frame
        img = Image.new("RGB", (640, 360), color=(18, 26, 22))
        draw = ImageDraw.Draw(img)

        # Draw crosshair grid and border
        draw.rectangle([10, 10, 630, 350], outline=(40, 180, 100), width=2)
        draw.line([320, 15, 320, 35], fill=(40, 180, 100), width=1)
        draw.line([320, 325, 320, 345], fill=(40, 180, 100), width=1)
        draw.line([15, 180, 35, 180], fill=(40, 180, 100), width=1)
        draw.line([605, 180, 625, 180], fill=(40, 180, 100), width=1)

        # Timestamp and metadata watermark
        time_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        draw.text((20, 20), f"[IBVAP BORDER SURVEILLANCE] {camera_id} - SECTOR B", fill=(0, 255, 128))
        draw.text((20, 35), f"TIME: {time_str} | MODE: IR NIGHT ENHANCED", fill=(200, 200, 200))
        draw.text((20, 50), f"EVENT: {event_title.upper()}", fill=(255, 70, 70))

        if plate_text:
            draw.text((20, 320), f"ANPR IDENT: {plate_text}", fill=(255, 220, 50))

        # Target bounding box
        if bbox and len(bbox) == 4:
            # Scale normalized coords
            bx1, by1, bx2, by2 = int(bbox[0] * 640), int(bbox[1] * 360), int(bbox[2] * 640), int(bbox[3] * 360)
            draw.rectangle([bx1, by1, bx2, by2], outline=(255, 50, 50), width=3)
            draw.text((bx1, max(0, by1 - 15)), f"TARGET CONF: 94%", fill=(255, 50, 50))
        else:
            # Default center box
            draw.rectangle([260, 120, 380, 260], outline=(255, 50, 50), width=3)
            draw.text((265, 100), "TARGET CONF: 94%", fill=(255, 50, 50))

        img.save(filepath, "JPEG", quality=85)
        return f"/storage/snapshots/{filename}"

evidence_capture = EvidenceCaptureService()
