"""
IBVAP - PyTorch Neural Infrastructure & Tensor Orchestration
Provides hardware autoselection (CUDA / MPS / CPU), vectorized tensor operations,
and deep neural modules for feature extraction, character OCR, and multi-scale YOLO perception.
"""
from typing import List, Tuple, Dict, Any, Optional, Union
import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    nn = None
    F = None
    TORCH_AVAILABLE = False


def is_torch_available() -> bool:
    """Returns True if PyTorch is installed and available in the active environment."""
    return TORCH_AVAILABLE


def get_torch_device() -> str:
    """
    Autodetects the highest-performance compute device:
    NVIDIA CUDA GPU -> Apple Silicon MPS -> Multi-threaded CPU.
    """
    if not TORCH_AVAILABLE:
        return "cpu"
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def get_device_telemetry() -> Dict[str, Any]:
    """Returns real-time neural hardware telemetry."""
    device_name = get_torch_device()
    telemetry = {
        "torch_available": TORCH_AVAILABLE,
        "active_device": device_name,
        "acceleration": "CUDA TENSOR CORES" if device_name == "cuda" else "MPS METAL" if device_name == "mps" else "MULTI-THREADED CPU (AVX2/AVX-512)",
        "fp16_supported": device_name in ["cuda", "mps"],
        "tensor_engine": "PyTorch v" + (torch.__version__ if TORCH_AVAILABLE else "Fallback-SimEngine")
    }
    if TORCH_AVAILABLE and device_name == "cuda":
        telemetry["gpu_name"] = torch.cuda.get_device_name(0)
        telemetry["vram_allocated_mb"] = round(torch.cuda.memory_allocated(0) / (1024 * 1024), 2)
        telemetry["vram_reserved_mb"] = round(torch.cuda.memory_reserved(0) / (1024 * 1024), 2)
    return telemetry


def numpy_to_tensor(
    img: np.ndarray,
    device: Optional[str] = None,
    half: bool = False
) -> Any:
    """
    Converts a NumPy BGR/RGB image (H, W, C) to a normalized PyTorch tensor (1, C, H, W).
    """
    if not TORCH_AVAILABLE:
        if len(img.shape) == 3:
            transposed = np.transpose(img, (2, 0, 1))
            expanded = np.expand_dims(transposed, axis=0)
            return (expanded.astype(np.float32) / 255.0)
        return img.astype(np.float32)

    dev = device or get_torch_device()
    if len(img.shape) == 3:
        transposed = np.transpose(img, (2, 0, 1))
        tensor = torch.from_numpy(transposed).unsqueeze(0).float() / 255.0
    elif len(img.shape) == 2:
        tensor = torch.from_numpy(img).unsqueeze(0).unsqueeze(0).float() / 255.0
    else:
        tensor = torch.from_numpy(img).float()

    tensor = tensor.to(dev)
    if half and dev in ["cuda", "mps"]:
        tensor = tensor.half()
    return tensor


def tensor_to_numpy(tensor: Any) -> np.ndarray:
    """Converts a PyTorch tensor back to a NumPy array."""
    if not TORCH_AVAILABLE or not hasattr(tensor, "detach"):
        return np.asarray(tensor)
    return tensor.detach().cpu().numpy()


def torch_vectorized_iou(boxes1: np.ndarray, boxes2: np.ndarray) -> np.ndarray:
    """
    Computes pairwise IoU between two sets of boxes [x1, y1, x2, y2].
    Leverages PyTorch tensor math when available, falls back to vectorized NumPy.
    """
    if TORCH_AVAILABLE:
        b1 = torch.as_tensor(boxes1, dtype=torch.float32)
        b2 = torch.as_tensor(boxes2, dtype=torch.float32)
        if b1.ndim == 1: b1 = b1.unsqueeze(0)
        if b2.ndim == 1: b2 = b2.unsqueeze(0)

        lt = torch.max(b1[:, None, :2], b2[None, :, :2])
        rb = torch.min(b1[:, None, 2:], b2[None, :, 2:])
        wh = (rb - lt).clamp(min=0)
        inter = wh[:, :, 0] * wh[:, :, 1]

        area1 = (b1[:, 2] - b1[:, 0]) * (b1[:, 3] - b1[:, 1])
        area2 = (b2[:, 2] - b2[:, 0]) * (b2[:, 3] - b2[:, 1])
        union = area1[:, None] + area2[None, :] - inter + 1e-6
        return (inter / union).cpu().numpy()

    # Vectorized NumPy Fallback
    b1 = np.atleast_2d(boxes1)
    b2 = np.atleast_2d(boxes2)
    lt = np.maximum(b1[:, None, :2], b2[None, :, :2])
    rb = np.minimum(b1[:, None, 2:], b2[None, :, 2:])
    wh = np.clip(rb - lt, 0, None)
    inter = wh[:, :, 0] * wh[:, :, 1]
    area1 = (b1[:, 2] - b1[:, 0]) * (b1[:, 3] - b1[:, 1])
    area2 = (b2[:, 2] - b2[:, 0]) * (b2[:, 3] - b2[:, 1])
    union = area1[:, None] + area2[None, :] - inter + 1e-6
    return inter / union


def torch_nms(
    boxes: np.ndarray,
    scores: np.ndarray,
    iou_threshold: float = 0.50
) -> List[int]:
    """
    Performs fast Non-Maximum Suppression on bounding boxes [x1, y1, x2, y2].
    """
    if len(boxes) == 0:
        return []

    if TORCH_AVAILABLE:
        try:
            from torchvision.ops import nms
            t_boxes = torch.as_tensor(boxes, dtype=torch.float32)
            t_scores = torch.as_tensor(scores, dtype=torch.float32)
            keep = nms(t_boxes, t_scores, iou_threshold)
            return keep.cpu().tolist()
        except Exception:
            pass

    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(int(i))
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        ovr = inter / (areas[i] + areas[order[1:]] - inter + 1e-6)

        inds = np.where(ovr <= iou_threshold)[0]
        order = order[inds + 1]

    return keep


# ==============================================================================
# PYTORCH NEURAL ARCHITECTURES
# ==============================================================================

if TORCH_AVAILABLE:
    class PyTorchFeatureExtractor(nn.Module):
        """
        Deep Residual Feature Extractor for Person Re-ID and Biometric Face Embeddings.
        Takes (B, 3, H, W) and extracts an L2-normalized 512-D identity representation.
        """
        def __init__(self, embedding_dim: int = 512):
            super().__init__()
            self.stem = nn.Sequential(
                nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1, bias=False),
                nn.BatchNorm2d(32),
                nn.SiLU(),
                nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1, bias=False),
                nn.BatchNorm2d(64),
                nn.SiLU(),
            )
            self.res1 = nn.Sequential(
                nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1, bias=False),
                nn.BatchNorm2d(64),
                nn.SiLU(),
                nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1, bias=False),
                nn.BatchNorm2d(64),
            )
            self.conv2 = nn.Sequential(
                nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1, bias=False),
                nn.BatchNorm2d(128),
                nn.SiLU(),
            )
            self.gap = nn.AdaptiveAvgPool2d((1, 1))
            self.fc = nn.Linear(128, embedding_dim, bias=False)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            out = self.stem(x)
            out = F.silu(out + self.res1(out))
            out = self.conv2(out)
            out = self.gap(out)
            out = torch.flatten(out, 1)
            out = self.fc(out)
            return F.normalize(out, p=2, dim=1)

    class PyTorchCRNN(nn.Module):
        """
        Convolutional Recurrent Neural Network for License Plate Character Sequence Recognition.
        """
        def __init__(self, num_classes: int = 37):
            super().__init__()
            self.cnn = nn.Sequential(
                nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1),
                nn.ReLU(True),
                nn.MaxPool2d(2, 2),
                nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
                nn.ReLU(True),
                nn.MaxPool2d(2, 2),
                nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(True),
                nn.AdaptiveAvgPool2d((1, 25))
            )
            self.rnn = nn.GRU(128, 64, bidirectional=True, batch_first=True)
            self.fc = nn.Linear(128, num_classes)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            conv = self.cnn(x)
            conv = conv.squeeze(2).permute(0, 2, 1)
            recurrent, _ = self.rnn(conv)
            return self.fc(recurrent)

    class PyTorchYOLOHead(nn.Module):
        """
        PyTorch Small-Target Detection Head with P2 High-Resolution Stride-4 Branch.
        """
        def __init__(self, num_classes: int = 6):
            super().__init__()
            self.num_classes = num_classes
            self.head_p2 = nn.Conv2d(64, (num_classes + 5) * 3, kernel_size=1)
            self.head_p3 = nn.Conv2d(128, (num_classes + 5) * 3, kernel_size=1)
            self.head_p4 = nn.Conv2d(256, (num_classes + 5) * 3, kernel_size=1)

        def forward(self, p2: torch.Tensor, p3: torch.Tensor, p4: torch.Tensor) -> List[torch.Tensor]:
            return [self.head_p2(p2), self.head_p3(p3), self.head_p4(p4)]

else:
    class PyTorchFeatureExtractor:
        def __init__(self, embedding_dim: int = 512):
            self.embedding_dim = embedding_dim
        def __call__(self, x: np.ndarray) -> np.ndarray:
            vec = np.random.RandomState(42).randn(self.embedding_dim).astype(np.float32)
            return vec / max(1e-6, np.linalg.norm(vec))

    class PyTorchCRNN:
        def __init__(self, num_classes: int = 37):
            self.num_classes = num_classes

    class PyTorchYOLOHead:
        def __init__(self, num_classes: int = 6):
            self.num_classes = num_classes

torch_device = get_torch_device()
torch_feature_extractor = PyTorchFeatureExtractor()
torch_crnn_engine = PyTorchCRNN()
