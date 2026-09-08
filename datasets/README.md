# IBVAP: Futuristic Multi-Spectral Border Surveillance Dataset

[![Standard](https://img.shields.io/badge/Standard-SIH%202026%20%7C%20SIH26187-blue.svg)](https://sih.gov.in)
[![Agency](https://img.shields.io/badge/Agency-SSB%20%2F%20MHA-darkgreen.svg)](https://mha.gov.in)
[![Modalities](https://img.shields.io/badge/Modalities-Optical%20%7C%20Thermal%20LWIR%20%7C%20ANPR-orange.svg)](#sensor-modalities)
[![Compliance](https://img.shields.io/badge/Compliance-DPDP%20Act%202023%20%C2%A78-brightgreen.svg)](#ethical--legal-compliance)

Defense-grade, multispectral synthetic computer vision and tracking dataset tailored for autonomous border security, real-time threat perception, and deep re-identification under the **Smart India Hackathon (SIH 2026)** problem statement **SIH26187** (Sashastra Seema Bal / Ministry of Home Affairs).

---

## 1. Directory Structure

```text
datasets/
├── README.md                          # Defense Dataset Specification Sheet (DSS)
├── data.yaml                          # YOLOv8 / YOLOv11 / YOLO26 training descriptor
├── dataset_manifest.json              # SHA-256 cryptographic verification manifest
│
├── raw/                               # Unprocessed multi-spectral sensor captures
│   ├── optical/                       # Day Optical (1280x720 25FPS) border perimeter frames
│   ├── thermal/                       # Long-Wave Infrared (LWIR 640x512 scaled) thermal heat frames
│   ├── anpr/                          # High-resolution checkpoint bumper & plate captures
│   └── faces/                         # High-fidelity biometric watchlist portraits
│
├── processed/                         # Standardized 640x640 model-ready tensors
│   ├── train/                         # Training partition (images & labels)
│   ├── val/                           # Validation partition (images & labels)
│   └── test/                          # Hold-out evaluation partition (images & labels)
│
├── annotations/                       # Interoperable multi-format ground truth
│   ├── classes.txt                    # Class ontology index
│   ├── dataset_stats.json             # Statistical distribution & object counts
│   ├── coco/instances_val.json        # Standard COCO JSON schema
│   ├── mot/gt.txt                     # MOT16/20 continuous multi-object tracking ground truth
│   ├── yolo/                          # Normalized bounding boxes (<cls> <cx> <cy> <w> <h>)
│   └── anpr/plates_gt.json            # Ground-truth Indian license plate metadata
│
├── test-videos/                       # 4 REAL playable tactical .mp4 video clips
│   ├── scenario_01_perimeter_breach.mp4      # Daylight fence breach & virtual wire trigger
│   ├── scenario_02_night_thermal_patrol.mp4  # Nighttime LWIR thermal white-hot infiltration probe
│   ├── scenario_03_checkpoint_anpr.mp4       # Checkpoint vehicle lane with plate recognition
│   └── scenario_04_multicam_handoff.mp4      # Cross-camera target transit (CAM-01 -> CAM-03)
│
└── scripts/
    ├── generate_datasets.py           # Autonomous reproducible generator
    └── verify_dataset.py              # Automated dataset integrity & video verification CLI
```

---

## 2. Sensor Modalities & Specifications

| Sensor Type | Resolution | Spectrum / Band | Frame Rate | Lens / FOV | Tactical Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Optical PTZ (CAM-01)** | 1920×1080 | Visible (400–700 nm) | 25.0 FPS | 4.8–120 mm (30x Optical Zoom) | Approach road & daylight perimeter breach detection |
| **Thermal LWIR (CAM-03)** | 640×512 (Scaled) | Long-Wave IR (8–14 μm) | 25.0 FPS | 25 mm Uncooled Microbolometer | Nighttime foliage penetration & human heat signature |
| **Checkpoint 4K (CAM-02)** | 3840×2160 | Visible / Starlight IR | 25.0 FPS | 8–32 mm Motorized Varifocal | Vehicle classification & high-confidence Indian ANPR |
| **Starlight NV (CAM-04)** | 1920×1080 | Low-Light Near-IR | 25.0 FPS | 0.0005 Lux F/1.2 Starlight | Low-light approach monitoring without active IR flood |

---

## 3. Annotation Ontology

The dataset conforms to 6 tactical border surveillance classes:

```text
0: person              # Border patrol guards, civilians, moving individuals
1: vehicle             # Checkpoint vehicles (Bolero, Gypsy, trucks, motorcycles)
2: license_plate       # Indian standard HSRP & military arrow registration plates
3: face                # Facial portrait crops for biometric watchlist correlation
4: intruder            # High-risk individuals in unauthorized restricted red zones
5: weapon_contraband   # Suspected carried payloads, wire cutters, weapons
```

### Supported Formats
1. **YOLO Format (`.txt`)**:
   ```text
   <class_id> <x_center> <y_center> <width> <height>
   0 0.450000 0.620000 0.060000 0.240000
   ```
2. **MOT16/20 Format (`gt.txt`)**:
   ```text
   <frame_id>,<track_id>,<bb_left>,<bb_top>,<bb_width>,<bb_height>,<conf>,<x>,<y>,<z>
   1,101,537,360,76,172,1.0,-1,-1,-1
   ```
3. **COCO Format (`instances_val.json`)**:
   Standard JSON schema containing `images`, `annotations`, `categories`, and `licenses`.
4. **Indian ANPR Format (`plates_gt.json`)**:
   Captures plate text, state jurisdiction code (DL, HR, UP, UK, WB, PB), vehicle model, and hotlist match justification.

---

## 4. Playable Tactical Test Videos

All 4 test videos in `test-videos/` are valid, self-contained H.264 / MP4 clips rendered at 25.0 FPS with active military HUD telemetry, timecode stamps, and GPS coordinates:

1. **`scenario_01_perimeter_breach.mp4`** (75 Frames, 1280×720):
   - Simulates daylight intruder advancing toward BOP Alpha fence line.
   - Demonstrates virtual tripwire intersection and immediate elevation from `PERIMETER_PROBE` to `CRITICAL_BREACH`.
2. **`scenario_02_night_thermal_patrol.mp4`** (75 Frames, 1280×720):
   - Simulates uncooled LWIR thermal white-hot sensor feed during zero-lux nighttime hours.
   - Accurately models heat emission differences between human bodies (37°C) and background terrain (18°C).
3. **`scenario_03_checkpoint_anpr.mp4`** (75 Frames, 1280×720):
   - Simulates vehicle entry lane at border inspection outpost.
   - Demonstrates automatic license plate extraction (`DL01AB1234`) and instant hotlist matching.
4. **`scenario_04_multicam_handoff.mp4`** (75 Frames, 1280×720):
   - Dual-camera split view demonstrating real-time target handoff between optical CAM-01 and thermal CAM-03 via the multi-camera directed graph topology.

---

## 5. Model Training Command

To train YOLOv8, YOLOv11, or YOLO26 on this dataset with Ultralytics:

```bash
# Launch single-command training
yolo detect train data=C:/Users/SAI CHARAN/OneDrive/Desktop/IBVAP/datasets/data.yaml model=yolo11n.pt epochs=50 imgsz=640 batch=16
```

---

## 6. Ethical & DPDP Act 2023 Compliance

This dataset was generated using the **IBVAP Autonomous Tactical Synthetic Engine**:
- **Zero Privacy Violation**: All human silhouettes, biometric face crops, and vehicle license plates are synthetically generated.
- **Section 8 Compliance (DPDP Act 2023)**: Ensures no unauthorized real personal data or surveillance recordings are leaked or stored.
- **Reproducibility**: Entire dataset can be re-synthesized or scaled at any time via `python datasets/scripts/generate_datasets.py`.
