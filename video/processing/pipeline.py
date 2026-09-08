"""
IBVAP - Video Processing & Frame Normalization Pipeline
"""
import time
from datetime import datetime, timezone
import cv2
import numpy as np
from typing import Tuple, Dict, Any

class VideoProcessingPipeline:
    """Preprocesses, enhances, and watermarks video frames for AI ingestion."""

    @staticmethod
    def letterbox(
        image: np.ndarray,
        target_shape: Tuple[int, int] = (640, 640),
        color: Tuple[int, int, int] = (114, 114, 114)
    ) -> Tuple[np.ndarray, float, Tuple[int, int]]:
        """
        Resizes and pads image while strictly maintaining aspect ratio.
        Returns (resized_image, scale_ratio, (pad_left, pad_top)).
        """
        shape = image.shape[:2] # [height, width]
        target_w, target_h = target_shape
        
        ratio = min(target_w / shape[1], target_h / shape[0])
        new_unpad = (int(round(shape[1] * ratio)), int(round(shape[0] * ratio)))
        
        dw = (target_w - new_unpad[0]) / 2
        dh = (target_h - new_unpad[1]) / 2
        
        if shape[::-1] != new_unpad:
            image = cv2.resize(image, new_unpad, interpolation=cv2.INTER_LINEAR)
            
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        
        image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
        return image, ratio, (left, top)

    @staticmethod
    def enhance_low_light(image: np.ndarray, clip_limit: float = 2.0) -> np.ndarray:
        """Applies Retinex gamma expansion & CLAHE for night-vision / thermal imagery."""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # CLAHE on luminance channel
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)
        
        # Merge back
        enhanced_lab = cv2.merge((l_enhanced, a, b))
        return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    @staticmethod
    def apply_hud_watermark(
        image: np.ndarray,
        camera_id: str,
        timestamp: Optional[float] = None,
        sensor_mode: str = "OPTICAL_IR"
    ) -> np.ndarray:
        """Overlays defense-grade military HUD telemetry on frame."""
        annotated = image.copy()
        h, w = annotated.shape[:2]
        
        ts_float = timestamp if timestamp is not None else time.time()
        time_str = datetime.fromtimestamp(ts_float, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-4] + " UTC"
        
        # Top watermark bar
        cv2.rectangle(annotated, (10, 10), (min(w - 10, 480), 45), (10, 15, 20), -1)
        cv2.rectangle(annotated, (10, 10), (min(w - 10, 480), 45), (40, 180, 100), 1)
        
        cv2.putText(annotated, f"SSB // IBVAP [{camera_id}] MODE: {sensor_mode}", (16, 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (40, 220, 120), 1, cv2.LINE_AA)
        cv2.putText(annotated, f"TIME: {time_str}", (16, 39),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32, (200, 210, 200), 1, cv2.LINE_AA)
        return annotated

    def process(
        self,
        frame: np.ndarray,
        camera_id: str,
        target_size: Tuple[int, int] = (640, 640),
        enhance: bool = False
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Executes full normalization, optional low-light boost, and HUD metadata."""
        enhanced = self.enhance_low_light(frame) if enhance else frame
        letterboxed, scale, pad = self.letterbox(enhanced, target_size)
        watermarked = self.apply_hud_watermark(letterboxed, camera_id)
        
        meta = {
            "camera_id": camera_id,
            "original_shape": frame.shape[:2],
            "target_shape": target_size,
            "scale_ratio": scale,
            "pad": pad,
            "enhanced": enhance
        }
        return watermarked, meta

video_pipeline = VideoProcessingPipeline()
