"""
IBVAP - OpenCV Night-Vision, CLAHE & Thermal Enhancement Engine
Applies adaptive histogram equalization in LAB color space, bilateral edge filtering,
and infrared false-color rendering for zero-lux military surveillance feeds.
"""
import cv2
import numpy as np

class LowLightEnhancer:
    """
    OpenCV-powered low-light and adverse weather enhancement pipeline.
    """
    def __init__(self, clip_limit: float = 3.0, tile_grid_size: tuple = (8, 8)):
        self.clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    def apply_clahe(self, frame: np.ndarray) -> np.ndarray:
        """
        Converts BGR to LAB, equalizes lightness (L channel) via CLAHE, and reconverts to BGR.
        Preserves natural chromaticity without color distortion.
        """
        if frame is None or frame.size == 0:
            return frame

        if len(frame.shape) == 2:
            return self.clahe.apply(frame)

        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l_clahe = self.clahe.apply(l)
        enhanced_lab = cv2.merge((l_clahe, a, b))
        return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    def enhance_night_frame(
        self,
        frame: np.ndarray,
        gamma: float = 1.6,
        denoise_bilateral: bool = True
    ) -> np.ndarray:
        """
        Multi-stage night-vision enhancement:
        1. CLAHE in LAB space to bring out dark details.
        2. Bilateral filtering for edge-preserving denoising.
        3. Gamma expansion for low-lux contrast illumination.
        """
        if frame is None or frame.size == 0:
            return frame

        # Stage 1: CLAHE
        enhanced = self.apply_clahe(frame)

        # Stage 2: Bilateral Denoising (preserves sharp perimeter wire/fence lines)
        if denoise_bilateral and len(frame.shape) == 3:
            enhanced = cv2.bilateralFilter(enhanced, d=5, sigmaColor=50, sigmaSpace=50)

        # Stage 3: Gamma expansion
        if abs(gamma - 1.0) > 0.05:
            inv_gamma = 1.0 / max(0.1, gamma)
            lut = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
            enhanced = cv2.LUT(enhanced, lut)

        return enhanced

    def generate_thermal_colormap(self, gray_frame: np.ndarray, colormap: int = cv2.COLORMAP_INFERNO) -> np.ndarray:
        """
        Generates tactical thermal infrared visualization (Inferno or Jet colormap).
        """
        if gray_frame is None or gray_frame.size == 0:
            return gray_frame

        if len(gray_frame.shape) == 3:
            gray = cv2.cvtColor(gray_frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = gray_frame

        normalized = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        return cv2.applyColorMap(normalized, colormap)

low_light_enhancer = LowLightEnhancer()
