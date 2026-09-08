"""
IBVAP - Image Enhancement & Denoising Engine
Removes CCTV sensor grain and sharpens perimeter fencing edges.
"""
import numpy as np

class ImageEnhancement:
    def enhance_contrast(self, frame: np.ndarray) -> np.ndarray:
        """Adaptive histogram contrast enhancement simulation."""
        if frame is None: return frame
        return np.clip(frame.astype(np.float32) * 1.15, 0, 255).astype(np.uint8)

image_enhancer = ImageEnhancement()
