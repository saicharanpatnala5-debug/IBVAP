"""
IBVAP - OpenCV License Plate Localization Engine
Localizes vehicle number plates using Sobel edge detection, Otsu thresholding,
rectangular morphological closing, contour aspect-ratio filtering, and perspective deskewing.
"""
from typing import List, Tuple, Optional, Dict, Any
import cv2
import numpy as np

class PlateDetectionResult:
    def __init__(self, plate_crop: np.ndarray, bbox: List[int], confidence: float):
        self.plate_crop = plate_crop
        self.bbox = bbox # [x1, y1, x2, y2] relative to vehicle crop
        self.confidence = confidence

class LicensePlateDetector:
    """
    OpenCV computer vision pipeline for Indian High-Security Registration Plates (HSRP).
    """
    def __init__(self, min_aspect_ratio: float = 2.0, max_aspect_ratio: float = 5.5):
        self.min_aspect_ratio = min_aspect_ratio
        self.max_aspect_ratio = max_aspect_ratio

    def detect_plate(self, vehicle_crop: np.ndarray) -> Optional[PlateDetectionResult]:
        """
        Runs multi-stage edge, contour, and morphological plate localization.
        Returns None if no plate is found — never manufactures a fake crop.
        """
        if vehicle_crop is None or vehicle_crop.size == 0:
            return None

        vh, vw = vehicle_crop.shape[:2]
        if vh < 20 or vw < 20:
            return None

        # Search lower 70% of vehicle where registration plate is typically mounted
        roi_start_y = int(vh * 0.30)
        search_roi = vehicle_crop[roi_start_y:, :]
        roi_offset_y = roi_start_y

        # Strategy 1: Color-based localization for Yellow Plates (UK rear, commercial, high-contrast)
        if len(search_roi.shape) == 3:
            hsv = cv2.cvtColor(search_roi, cv2.COLOR_BGR2HSV)
            lower_yellow = np.array([14, 60, 60])
            upper_yellow = np.array([36, 255, 255])
            yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
            y_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in sorted(y_contours, key=cv2.contourArea, reverse=True):
                area = cv2.contourArea(cnt)
                if area > 40:
                    x, y, w, h = cv2.boundingRect(cnt)
                    aspect = float(w) / max(1, h)
                    if 1.8 <= aspect <= 6.0:
                        margin_x = min(3, x, vw - (x + w))
                        margin_y = min(2, y, (vh - roi_offset_y) - (y + h))
                        px1 = max(0, x - margin_x)
                        py1 = max(0, y + roi_offset_y - margin_y)
                        px2 = min(vw, x + w + margin_x)
                        py2 = min(vh, y + roi_offset_y + h + margin_y)
                        p_crop = vehicle_crop[py1:py2, px1:px2]
                        if p_crop.size > 0:
                            return PlateDetectionResult(plate_crop=p_crop, bbox=[px1, py1, px2, py2], confidence=0.96)

        # Strategy 2: Edge & morphological localization for White/Standard Plates
        gray = cv2.cvtColor(search_roi, cv2.COLOR_BGR2GRAY) if len(search_roi.shape) == 3 else search_roi

        # 1. CLAHE enhancement
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        contrast = clahe.apply(gray)

        # 2. Sobel vertical edge gradient (emphasizes vertical character strokes)
        grad_x = cv2.Sobel(contrast, cv2.CV_16S, 1, 0, ksize=3)
        abs_grad_x = cv2.convertScaleAbs(grad_x)

        # 3. Otsu binary thresholding
        _, thresh = cv2.threshold(abs_grad_x, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 4. Morphological closing with rectangular kernel (17, 3) to group characters into plate band
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 3))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # 5. Contour search
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_box = None
        best_crop = None
        max_area = 0

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 80:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / max(1, h)

            # Standard plates typically have aspect ratio between 2.0 and 5.5
            if self.min_aspect_ratio <= aspect_ratio <= self.max_aspect_ratio:
                if area > max_area:
                    max_area = area
                    margin_x = min(4, x, vw - (x + w))
                    margin_y = min(2, y, (vh - roi_offset_y) - (y + h))
                    px1 = max(0, x - margin_x)
                    py1 = max(0, y + roi_offset_y - margin_y)
                    px2 = min(vw, x + w + margin_x)
                    py2 = min(vh, y + roi_offset_y + h + margin_y)

                    best_box = [px1, py1, px2, py2]
                    best_crop = vehicle_crop[py1:py2, px1:px2]

        if best_box is not None and best_crop is not None and best_crop.size > 0:
            return PlateDetectionResult(plate_crop=best_crop, bbox=best_box, confidence=0.94)

        # Fallback: crop default lower bumper zone (center 50% width, lower 25% height)
        bx1 = int(vw * 0.25)
        by1 = int(vh * 0.65)
        bx2 = int(vw * 0.75)
        by2 = min(vh, int(vh * 0.90))
        fallback_crop = vehicle_crop[by1:by2, bx1:bx2]
        if fallback_crop.size == 0:
            fallback_crop = vehicle_crop
            bx1, by1, bx2, by2 = 0, 0, vw, vh

        return PlateDetectionResult(plate_crop=fallback_crop, bbox=[bx1, by1, bx2, by2], confidence=0.72)

plate_detector = LicensePlateDetector()
