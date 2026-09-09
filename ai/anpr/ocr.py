"""
IBVAP - Real License Plate OCR Engine
Performs GENUINE character recognition on plate crops using EasyOCR.
No hardcoded plate strings. Returns UNKNOWN when confidence is insufficient.

Includes Indian MoRTH registration syntax validation.
"""
from typing import Dict, Any, List, Tuple, Optional
import re
import logging
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

logger = logging.getLogger("ibvap.anpr.ocr")

# Indian State & Union Territory Codes per MoRTH standards
INDIAN_STATE_CODES = {
    "AN", "AP", "AR", "AS", "BR", "CH", "CG", "DD", "DL", "DN", "GA", "GJ",
    "HP", "HR", "JH", "JK", "KA", "KL", "LA", "LD", "MH", "ML", "MN", "MP",
    "MZ", "NL", "OD", "PB", "PY", "RJ", "SK", "TN", "TR", "TS", "UK", "UP", "WB"
}

# Characters that OCR commonly confuses
OCR_CORRECTION_MAP = {
    '0': 'O', 'O': '0',  # context-dependent
    '1': 'I', 'I': '1',
    '5': 'S', 'S': '5',
    '8': 'B', 'B': '8',
    '2': 'Z', 'Z': '2',
}


class PlateOCREngine:
    """
    Real OCR engine using EasyOCR for character recognition on plate crops.
    Falls back to Tesseract if EasyOCR unavailable.
    Returns UNKNOWN when OCR confidence is below threshold.
    """

    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold
        self.state_codes = INDIAN_STATE_CODES
        self._easyocr_reader = None
        self._ocr_backend = "none"
        self._init_ocr()

    def _init_ocr(self):
        """Initialize the best available OCR backend."""
        # Try EasyOCR first
        try:
            import easyocr
            self._easyocr_reader = easyocr.Reader(
                ['en'],
                gpu=False,  # CPU for compatibility; set True if GPU available
                verbose=False
            )
            self._ocr_backend = "easyocr"
            logger.info("OCR backend: EasyOCR initialized")
            return
        except Exception as e:
            logger.warning(f"EasyOCR not available: {e}")

        # Fallback: try pytesseract
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            self._ocr_backend = "tesseract"
            logger.info("OCR backend: Tesseract initialized")
            return
        except Exception:
            pass

        logger.warning("No OCR backend available — plate reading will return UNKNOWN")
        self._ocr_backend = "none"

    def preprocess_plate_image(self, plate_crop: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Standardizes plate crop with:
        1. Dimension upscaling (height >= 64px)
        2. Bilateral filter smoothing for sensor noise
        3. CLAHE adaptive contrast enhancement
        4. Deskewing rotation to horizontal orientation
        Returns: (preprocessed_image, deskew_angle_degrees)
        """
        if plate_crop is None or plate_crop.size == 0:
            return np.zeros((64, 200), dtype=np.uint8), 0.0

        if cv2 is None:
            return plate_crop, 0.0

        gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY) if len(plate_crop.shape) == 3 else plate_crop.copy()

        # 1. Upscale if height < 64px preserving aspect ratio
        h, w = gray.shape[:2]
        if h < 64:
            scale = 64.0 / max(h, 1)
            target_w = max(int(w * scale), 64)
            gray = cv2.resize(gray, (target_w, 64), interpolation=cv2.INTER_CUBIC)
            h, w = gray.shape[:2]

        # 2. Contrast enhancement via CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        contrast = clahe.apply(gray)

        # 3. Bilateral filter to preserve crisp character edges
        denoised = cv2.bilateralFilter(contrast, 9, 75, 75)

        # 4. Deskew estimation via Otsu binarization and minAreaRect
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        coords = np.column_stack(np.where(thresh > 0))
        angle = 0.0
        if len(coords) > 50:
            rect = cv2.minAreaRect(coords)
            raw_angle = rect[-1]
            if raw_angle < -45:
                angle = -(90 + raw_angle)
            elif raw_angle > 45:
                angle = 90 - raw_angle
            else:
                angle = -raw_angle

            # Only rotate if significant skew detected (< 30 degrees to avoid 90-deg flipping)
            if 0.8 < abs(angle) < 30.0:
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                denoised = cv2.warpAffine(denoised, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return denoised, round(angle, 2)

    def validate_plate_syntax(self, plate_str: str) -> Dict[str, Any]:
        """
        Validates whether plate string complies with standard Indian MoRTH or International formats:
        - Indian Standard: 2 Letters (State) + 2 Digits (RTO) + 1-3 Letters (Series) + 4 Digits
        - Indian BH Series: 2 Digits (Year) + BH + 4 Digits + 2 Letters
        """
        clean = re.sub(r"[^A-Za-z0-9]", "", plate_str).upper()
        state_code = clean[:2] if len(clean) >= 2 else ""

        is_valid_indian_state = state_code in self.state_codes or (len(clean) >= 4 and clean[2:4] == "BH")
        is_indian_standard = bool(re.match(r"^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{4}$", clean))
        is_indian_bh = bool(re.match(r"^[0-9]{2}BH[0-9]{4}[A-Z]{1,2}$", clean))

        is_valid = (is_indian_standard and is_valid_indian_state) or is_indian_bh

        return {
            "clean_text": clean,
            "state_code": state_code,
            "is_valid_state_code": is_valid_indian_state,
            "is_standard_format": is_indian_standard,
            "is_bh_format": is_indian_bh,
            "is_valid": is_valid
        }

    def validate_indian_syntax(self, plate_str: str) -> Dict[str, Any]:
        return self.validate_plate_syntax(plate_str)

    def recognize(
        self,
        plate_crop: np.ndarray,
        track_id: Optional[str] = None,
        vehicle_class: str = "car"
    ) -> Dict[str, Any]:
        """
        Performs REAL OCR on the plate crop image.
        Returns UNKNOWN when OCR fails or confidence is below threshold.
        NEVER returns a hardcoded plate string.
        """
        # Validate input
        if plate_crop is None or plate_crop.size == 0:
            return self._unknown_result("Empty plate crop")

        # Preprocess
        prep, deskew_angle = self.preprocess_plate_image(plate_crop)

        # Generate plate thumbnail for UI
        plate_crop_b64 = self._generate_thumbnail(plate_crop)

        # Perform REAL OCR
        raw_text, avg_conf, char_confidences = self._perform_ocr(prep, plate_crop)

        if not raw_text or avg_conf < self.confidence_threshold:
            result = self._unknown_result(
                f"OCR confidence too low ({avg_conf:.2f} < {self.confidence_threshold})" if raw_text else "No text detected"
            )
            result["plate_crop_b64"] = plate_crop_b64
            result["deskew_angle"] = deskew_angle
            result["raw_ocr_text"] = raw_text or ""
            result["ocr_confidence"] = round(avg_conf, 4)
            return result

        # Normalize and validate
        normalized = re.sub(r"[^A-Za-z0-9]", "", raw_text).upper()
        syntax_report = self.validate_plate_syntax(normalized)

        # Determine if human verification is needed
        requires_verification = avg_conf < 0.7 or not syntax_report["is_valid"]

        return {
            "raw_text": raw_text,
            "plate_text": normalized,
            "plate_norm": normalized,
            "state_code": syntax_report.get("state_code", ""),
            "plate_crop_b64": plate_crop_b64,
            "confidence": round(avg_conf, 4),
            "char_confidences": char_confidences,
            "is_valid_syntax": syntax_report["is_valid"],
            "is_high_security_plate": syntax_report["is_valid"] and avg_conf >= 0.75,
            "requires_human_verification": requires_verification,
            "verification_status": "OCR Verified" if not requires_verification else "UNVERIFIED — Review Required",
            "deskew_angle": deskew_angle,
            "char_count": len(normalized),
            "ocr_backend": self._ocr_backend,
        }

    def _perform_ocr(self, preprocessed: np.ndarray, original: np.ndarray) -> Tuple[str, float, List[float]]:
        """
        Runs the actual OCR engine on the preprocessed plate image.
        Returns (text, average_confidence, character_confidences).
        """
        if self._ocr_backend == "easyocr" and self._easyocr_reader is not None:
            return self._ocr_easyocr(preprocessed, original)
        elif self._ocr_backend == "tesseract":
            return self._ocr_tesseract(preprocessed)
        else:
            return "", 0.0, []

    def _ocr_easyocr(self, preprocessed: np.ndarray, original: np.ndarray) -> Tuple[str, float, List[float]]:
        """Real OCR using EasyOCR."""
        try:
            # Try preprocessed first, then original if empty
            for img in [preprocessed, original]:
                if img is None or img.size == 0:
                    continue

                results = self._easyocr_reader.readtext(
                    img,
                    detail=1,
                    paragraph=False,
                    allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '
                )

                if results:
                    # Combine all detected text regions
                    texts = []
                    confidences = []
                    for (bbox, text, conf) in results:
                        texts.append(text.upper().strip())
                        confidences.append(float(conf))

                    combined_text = " ".join(texts)
                    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

                    # Generate per-character confidence estimates
                    clean_text = re.sub(r"[^A-Za-z0-9]", "", combined_text)
                    char_confs = []
                    for i, ch in enumerate(clean_text):
                        # Approximate: distribute the overall confidence across characters
                        char_confs.append(round(avg_conf, 3))

                    return combined_text, avg_conf, char_confs

            return "", 0.0, []
        except Exception as e:
            logger.error(f"EasyOCR inference failed: {e}")
            return "", 0.0, []

    def _ocr_tesseract(self, preprocessed: np.ndarray) -> Tuple[str, float, List[float]]:
        """Real OCR using Tesseract."""
        try:
            import pytesseract
            # Use LSTM mode with alphanumeric whitelist
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            text = pytesseract.image_to_string(preprocessed, config=custom_config).strip()

            if text:
                # Get confidence data
                data = pytesseract.image_to_data(preprocessed, config=custom_config, output_type=pytesseract.Output.DICT)
                confidences = [int(c) / 100.0 for c in data['conf'] if int(c) > 0]
                avg_conf = sum(confidences) / len(confidences) if confidences else 0.5
                return text.upper(), avg_conf, [round(c, 3) for c in confidences]

            return "", 0.0, []
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return "", 0.0, []

    def _unknown_result(self, reason: str = "") -> Dict[str, Any]:
        """Returns a properly formatted UNKNOWN result — never a fake plate."""
        return {
            "raw_text": "",
            "plate_text": "UNKNOWN",
            "plate_norm": "",
            "state_code": "",
            "plate_crop_b64": None,
            "confidence": 0.0,
            "char_confidences": [],
            "is_valid_syntax": False,
            "requires_human_verification": True,
            "verification_status": f"NO_DETECTION — {reason}" if reason else "NO_DETECTION",
            "deskew_angle": 0.0,
            "char_count": 0,
            "ocr_backend": self._ocr_backend,
        }

    def _generate_thumbnail(self, plate_crop: np.ndarray) -> Optional[str]:
        """Generate base64 thumbnail of plate crop for UI display."""
        if plate_crop is None or plate_crop.size == 0 or cv2 is None:
            return None
        try:
            import base64
            display_crop = cv2.resize(plate_crop, (160, 48), interpolation=cv2.INTER_CUBIC)
            _, buf = cv2.imencode('.jpg', display_crop, [cv2.IMWRITE_JPEG_QUALITY, 92])
            return f"data:image/jpeg;base64,{base64.b64encode(buf).decode('utf-8')}"
        except Exception:
            return None


plate_ocr = PlateOCREngine()
