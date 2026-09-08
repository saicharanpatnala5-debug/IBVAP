# IBVAP // Intelligent Border Video Analytics Platform
> **Software-Defined AI Intelligence Transforming Legacy CCTV into Autonomous Border Surveillance**

[![Standard](https://img.shields.io/badge/Standard-SIH%202026%20%7C%20SIH26187-0ea5e9?style=for-the-badge)](https://sih.gov.in)
[![Agency](https://img.shields.io/badge/Agency-SSB%20%2F%20MHA%20Police--II-10b981?style=for-the-badge)](https://mha.gov.in)
[![Security](https://img.shields.io/badge/Compliance-DPDP%20Act%202023%20%C2%A78-8b5cf6?style=for-the-badge)](#ethical--legal-compliance)
[![Deployment](https://img.shields.io/badge/Deployment-Air--Gapped%20%7C%20Edge--Native-f59e0b?style=for-the-badge)](#air-gapped-deployment)
[![Tests](https://img.shields.io/badge/Tests-42%2F42%20Passing-emerald?style=for-the-badge)](#system-verification)

---

## 1. Executive Mission & Problem Space

Conventional CCTV across **Border Out Posts (BOPs)**, international riverine corridors, and forward checkpoints forces operators into hours of manual visual monitoring. Fatigue sets in within 20 minutes, allowing covert intrusions, loitering probes, and smuggling drops to go unnoticed.

**IBVAP** solves this by converting existing legacy IP/RTSP CCTV streams into an autonomous, event-driven perception and response network without requiring camera replacements.

```text
  [ Legacy RTSP Cameras ] ──► [ Video Ingestion Pipeline ] ──► [ Multi-Stage AI Perception ]
         (Optical / Thermal)          (Zero-Lag Ring Buffer)           (YOLO26 + ByteTrack)
                                                                               │
  [ Instant Tactical Dispatch ] ◄── [ Calibrated Risk Engine ] ◄── [ Spatial-Temporal Fusion ]
    (WebSocket / Radio / HUD)         (Explainable AI Card)           (Incident Synthesizer)
```

Instead of sending disjointed alerts like *"Person detected"*, IBVAP generates contextual military intelligence:
> *"Target Alpha-901 disembarked from Vehicle DL01AB1234 near Camera 01 at 02:14:32. Crossed virtual perimeter into Restricted Red Zone, loitered for 28s, and initiated an inward vector toward the command post. Risk Engine evaluated severity as CRITICAL (Score: 125). Directed Topology Graph predicts transit to Camera 03 (Probability: 78%, ETA: 15–45s)."*

---

## 2. Core Architectural Pillars

### I. Mathematical Risk Scoring Engine
Calculates calibrated threat probabilities across multi-factor inputs:
$$	ext{Risk Score } R = \min\left(100, \; \sum_{i=1}^{n} w_i \cdot c_i \cdot \mathbb{I}(	ext{factor}_i) + \Delta_{	ext{compound}}ight)$$
*Where $w_i \in \{30, 15, 15, 20, 20, 10\}$ represent weights for Restricted Zone, Night Curfew, Dwell/Loitering, Inward Heading, Hotlist Plate, and Multi-Entity Coordination.*

### II. 8-State Kalman Trajectory Engine
Tracks targets continuously through occlusions and erratic movement using an 8-dimensional state vector:
$$\mathbf{x} = [u, v, \gamma, h, \dot{u}, \dot{v}, \dot{\gamma}, \dot{h}]^T$$
Where $(u, v)$ is the bounding box center, $\gamma$ is aspect ratio, $h$ is height, and $(\dot{u}, \dot{v}, \dot{\gamma}, \dot{h})$ represent respective velocities.

### III. Directed Multi-Camera Topology & Predictive Handoff
Models the physical terrain as a weighted directed graph $G = (V, E)$. Predicts candidate camera transitions:
$$P(	ext{Transit } C_i 	o C_j \mid \Delta t) = \mathcal{N}\left(\Delta t \mid \mu_{ij}, \sigma_{ij}^2ight) \cdot T_{ij}$$

### IV. Air-Gapped Offline Resilience
Equipped with an autonomous SQLite WAL offline queue supporting up to **50,000 local records**, an encrypted AES-256 local ring buffer, and prioritized 4-tier upstream syncing once communication links recover.

---

## 3. Subsystem Directory Map

```text
IBVAP/
├── docs/            # Defense PRD, TDD with mathematical proofs, 300 DPI architecture diagrams, API specs
├── ai/              # Perception stack: detection, ByteTrack, YuNet/SFace, ANPR, behavior, risk engine
├── backend/         # FastAPI production server, 17 routers, 12 async models, WebSocket broadcasting
├── video/           # RTSP client with circuit breakers, Retinex/CLAHE enhancement, SHA-256 evidence recorder
├── database/        # 14 relational tables, 3 views, 3 versioned migrations, 5 tactical SQL seeds, ER diagram
├── configs/         # Production YAML configurations for cameras, security zones, models, and risk rules
├── edge/            # Multi-arch edge daemon (x86 & Jetson), 50k offline WAL queue, priority sync manager
├── datasets/        # 106 files: raw multispectral data, 640x640 YOLO splits, 4 playable tactical MP4 videos
├── deployment/      # Production Docker Compose, Nginx reverse proxy, Prometheus/Grafana, systemd units
├── scripts/         # Setup automation (.sh/.bat/.ps1), database seeders, stream testers, latency auditor
└── storage/         # Cryptographically sealed tactical HUD evidence snapshots and video clips
```

---

## 4. Quickstart & Deployment

### Option A: Complete Docker Compose Production Stack
```bash
# Clone and navigate to deployment scripts
cd deployment/scripts

# On Windows:
deploy.bat
# On Linux / macOS:
bash deploy.sh
```

### Option B: Standalone Native Python
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Provision and seed tactical database
python scripts/seed_db.py

# 3. Launch Central Command Server
python run.py

# 4. Launch Autonomous Forward Edge Daemon
python -m edge.main --duration 60
```

---

## 5. Live Demonstration & Portals

- **Interactive Command API (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Live SIH 8-Step Pitch Scenario**: `POST http://localhost:8000/api/demo/run-scenario`
- **Real-Time Telemetry & Alert WebSockets**: `ws://localhost:8000/ws/alerts` & `ws://localhost:8000/ws/telemetry`
- **Grafana Security Operations Center**: [http://localhost:3000](http://localhost:3000) (`commandant` / `TacticalCommand2026!`)
- **Prometheus Metric Exporter**: [http://localhost:9090](http://localhost:9090)

---

## 6. System Verification

All **42 automated test suites** execute in **5.19 seconds**:

```bash
# Execute full test suite
pytest backend/tests/ -v
```

---

## 7. Ethical & Legal Compliance

- **DPDP Act 2023 (§8)**: All personal data handling enforces cryptographic pseudonymization, immutable audit chains, and automated retention purges.
- **Explainable AI (XAI)**: Every automated risk alert includes an explainability breakdown to guarantee human-in-the-loop oversight by Sashastra Seema Bal command personnel.
