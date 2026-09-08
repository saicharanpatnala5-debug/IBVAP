# Pretrained Detection Models Directory
Place your Ultralytics YOLO26 / YOLO11 model weights here:
- `yolo26n.pt` (Lightweight edge baseline)
- `yolo26s.pt` (Recommended SIH balance)
- `yolo26m.pt` (High-accuracy server model)

Export to ONNX for 3x faster CPU execution:
```bash
yolo export model=yolo26s.pt format=onnx imgsz=640
```
