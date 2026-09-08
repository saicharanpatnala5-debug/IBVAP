# IBVAP: Intelligent Border Video Analytics Platform
### Software-Defined AI Video Intelligence for Existing CCTV Infrastructure
**Smart India Hackathon (SIH 2026) | Problem Statement: SIH26187**
*Ministry of Home Affairs / Sashastra Seema Bal (SSB), Police-II Division*

---

## 1. Executive Summary & Core Value Proposition
Conventional CCTV surveillance across Border Out Posts (BOPs), checkposts, and strategic military installations places an overwhelming monitoring burden on human operators. Standard cameras produce endless raw footage requiring continuous visual surveillance.

**IBVAP transforms legacy IP CCTV into an intelligent, event-driven situational surveillance network without requiring camera hardware replacement.**

Instead of just reporting *"Person detected"*, IBVAP provides full situational intelligence:
> *"Vehicle V-402 disembarked Target P-107 near Camera 01 at 02:14:32. Target crossed the virtual fence into the Restricted Red Zone at night, remained stationary for 28 seconds (loitering), and initiated an inward vector toward the command post. Context-Aware Risk Engine evaluated severity as CRITICAL (Risk Score: 125). Multi-Camera Graph Topology predicts target transit to Camera 03 (78% probability, ETA 15–45s)."*

---

## 2. Key Differentiating Features (Why IBVAP Wins SIH)

1. **AI Event Fusion (PRD Section 16)**:
   - Replaces alert fatigue by correlating multiple raw detections into a single chronological `Incident` rather than firing dozens of disconnected alarms.
2. **Explainable AI Alert Cards (TDD Section 10)**:
   - Every alert answers **WHAT, WHO, WHERE, WHEN, WHY, CONFIDENCE,** and provides an **EVIDENCE SNAPSHOT**.
3. **Multi-Camera Topology & Predictive Camera Handoff**:
   - Models the site as a directed graph. Predicts candidate next cameras based on transition probabilities and transit time windows.
4. **Context-Aware Risk Engine**:
   - Calibrated multi-factor scoring: Restricted Zone (+30), Night context (+15), Loitering (+15), Inward direction vector (+20), Unknown vehicle plate (+20), Multi-entity coordination (+10).
5. **Software-Defined ANPR Pipeline**:
   - OCR text normalization, character confidence filtering, and multi-frame voting.
6. **Edge-First Offline Resilience**:
   - Local buffer queue stores events during communication blackouts and automatically synchronizes when connectivity is restored.
7. **DPDP Act 2023 Compliance & Security**:
   - Immutable audit logs for all security actions, JWT authentication, and strict Role-Based Access Control (Admin, Supervisor, Operator, Auditor).
8. **Interactive SIH Demonstration Simulator**:
   - Includes a built-in 8-step live pitch runner (`/api/demo/run-scenario`) that allows zero-dependency presentation to judges.

---

## 3. Architecture Overview

```text
               EXISTING IP CCTV INFRASTRUCTURE
                            │
                            ▼
              RTSP / Video Stream Ingestion
                            │
                            ▼
                     AI Perception
          (YOLO Detection + ByteTrack Trajectory)
                            │
                            ▼
                  Scene Intelligence
     (Virtual Fence + Dwell/Loitering + Inward Vector)
                            │
                            ▼
                 AI Event Fusion Engine
       (Chronological Correlation & Incident Synthesis)
                            │
                            ▼
               Context-Aware Risk Engine
      (Weighted Factors -> Normal / Low / Medium / High / Critical)
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
    Actionable Alerts             Command Dashboard
   (Explainable AI Cards)        (FastAPI REST + WebSockets)
```

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Pip

### Installation
```bash
# Navigate to backend directory
cd ibvap-backend

# Install dependencies
pip install -r requirements.txt

# Seed the database with realistic BOP Alpha Sector B demo data
python scripts/seed_data.py

# Launch the FastAPI server
python scripts/run_server.py
```

Server starts at: **`http://127.0.0.1:8000`**
Interactive Swagger API Docs: **`http://127.0.0.1:8000/docs`**

---

## 5. Live SIH Demo Pitch Execution

You can trigger the full 8-step demonstration in one click or execute it step-by-step during your pitch:

### Execute Complete 8-Step Story:
```bash
curl -X POST http://127.0.0.1:8000/api/demo/run-scenario
```

### Or Step-by-Step for Presentation:
- **Step 1**: Baseline Normal Operations (`POST /api/demo/step/1`)
- **Step 2**: Vehicle Arrival & ANPR Identification (`POST /api/demo/step/2`)
- **Step 3**: Person Disembarkation near Boundary (`POST /api/demo/step/3`)
- **Step 4**: Virtual Fence Restricted Zone Intrusion at Night (`POST /api/demo/step/4`)
- **Step 5**: Prolonged Loitering (>25s) & Inward Vector (`POST /api/demo/step/5`)
- **Step 6**: Context-Aware Risk Engine Classification (`POST /api/demo/step/6`)
- **Step 7**: AI Event Fusion & Critical Explainable Alert Card (`POST /api/demo/step/7`)
- **Step 8**: Predictive Camera Handoff to Camera 03 (`POST /api/demo/step/8`)

---

## 6. Running Automated Tests
```bash
pytest tests/ -v
```

---

## 7. API Reference Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Authenticate and obtain JWT token |
| `GET` | `/api/cameras` | List all registered CCTV cameras with online status |
| `GET` | `/api/cameras/{id}/predict-handoff` | Compute predictive next camera transit |
| `GET` | `/api/cameras/topology/graph` | Fetch site camera topological network graph |
| `POST` | `/api/zones` | Define polygonal restricted / monitoring virtual fence |
| `POST` | `/api/events/ingest-detection` | Ingest detection, calculate dwell and zone collision |
| `GET` | `/api/incidents` | List fused security incidents |
| `GET` | `/api/incidents/{id}` | Incident detail with full chronological timeline |
| `GET` | `/api/alerts` | Active alert rail with Explainable AI Cards |
| `POST` | `/api/alerts/{id}/ack` | Operator alert acknowledgement and audit log |
| `GET` | `/api/anpr/plates` | Search vehicle license plates and OCR confidence |
| `POST` | `/api/search` | Video Intelligence Search across metadata |
| `GET` | `/api/health/summary` | Camera and system telemetry (FPS, latency, loss) |
| `GET` | `/api/audit` | DPDP Act 2023 compliance audit trail |
| `WS` | `/ws/alerts` | Real-time WebSocket alert and telemetry stream |
