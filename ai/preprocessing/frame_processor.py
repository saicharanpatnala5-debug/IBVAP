"""
IBVAP - OpenCV Frame Geometry & Motion Processing
Implements letterboxing, perspective unwarping, and MOG2 background motion subtraction.
"""
import cv2
import numpy as np
from typing import Tuple, List, Optional

class FrameProcessor:
    def __init__(self):
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

    def letterbox(
        self,
        img: np.ndarray,
        new_shape: Tuple[int, int] = (640, 640),
        color: Tuple[int, int, int] = (114, 114, 114)
    ) -> Tuple[np.ndarray, float, Tuple[int, int]]:
        """
        Resizes and pads image to target shape while preserving aspect ratio.
        Returns: (padded_img, scale_ratio, (pad_left, pad_top))
        """
        if img is None:
            return np.zeros((new_shape[0], new_shape[1], 3), dtype=np.uint8), 1.0, (0, 0)

        shape = img.shape[:2] # [h, w]
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        new_unpad = (int(round(shape[1] * r)), int(round(shape[0] * r)))
        dw = new_shape[1] - new_unpad[0]
        dh = new_shape[0] - new_unpad[1]

        dw /= 2 # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)

        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
        return img, r, (left, top)

    def unwarp_perspective(
        self,
        img: np.ndarray,
        src_points: np.ndarray,
        target_size: Tuple[int, int] = (400, 200)
    ) -> np.ndarray:
        """
        Performs four-point perspective transform to deskew angled camera views (e.g. ANPR plates).
        """
        dst_points = np.array([
            [0, 0],
            [target_size[0] - 1, 0],
            [target_size[0] - 1, target_size[1] - 1],
            [0, target_size[1] - 1]
        ], dtype=np.float32)

        M = cv2.getPerspectiveTransform(src_points.astype(np.float32), dst_points)
        warped = cv2.warpPerspective(img, M, target_size, flags=cv2.INTER_CUBIC)
        return warped

    def detect_motion_mask(self, frame: np.ndarray) -> np.ndarray:
        """Computes foreground moving object mask using MOG2 background subtraction."""
        if frame is None:
            return np.zeros((10, 10), dtype=np.uint8)
        return self.bg_subtractor.apply(frame)

frame_processor = FrameProcessor()
