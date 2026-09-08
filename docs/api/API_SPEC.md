# IBVAP: REST API & WebSocket Technical Specification
**Intelligent Border Video Analytics Platform — OpenAPI 3.1 Specification**  
*SIH 2026 Defense Architecture — Problem Statement SIH26187*  
*Base URL:* `http://127.0.0.1:8000` | *WebSocket URL:* `ws://127.0.0.1:8000`  
*Authentication:* `Bearer <JWT-Token>` via HTTP Header `Authorization: Bearer <token>`

---

## 1. Authentication & Security Architecture

All API endpoints (except `/api/health`, `/api/auth/login`, and Swagger docs `/docs`) require an authenticated JSON Web Token (JWT). Pass the token in the `Authorization` request header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 1.1 Role-Based Access Control (RBAC) Matrix

| Security Role | Description & Operational Clearances | Allowed Endpoints |
|---|---|---|
| `admin` | System Administrator (Full access, user provisioning, key rotation) | **All 43 endpoints** |
| `supervisor` | Outpost Commander / Inspector (Zone configuration, watchlist editing, incident resolution) | Cameras, Zones, Incidents, Watchlists, Health |
| `cctv_operator` | Operations Room Operator (Live feed monitoring, alert acknowledgment) | Alerts, Incidents (Read/Ack), ANPR Search |
| `field_response` | Quick Reaction Team (QRT) Mobile Lead (Receives tactical alert notifications) | Alerts (Read/Ack), Live Snapshots, Handoff |
| `auditor` | Statutory DPDP & MHA Compliance Officer (Chain-of-custody verification) | Audit Logs, Hash-Chain Verification, System Health |

---

## 2. API Endpoints Reference (43 Endpoints across 11 Routers)

### 2.1 Authentication Router (`/api/auth`)

#### `POST /api/auth/login`
- **Description:** Authenticates operator credentials and issues an 8-hour signed JWT bearer token.
- **Request Body (`application/x-www-form-urlencoded`):**
  ```text
  username=admin&password=AdminSecurePassword2026!
  ```
- **Response `200 OK` (`application/json`):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 28800,
    "user": {
      "username": "admin",
      "role": "admin",
      "full_name": "SSB Director General Ops"
    }
  }
  ```

#### `POST /api/auth/register`
- **Description:** Registers a new operator account (Requires `admin` role).
- **Request Body (`application/json`):**
  ```json
  {
    "username": "bop_inspector_singh",
    "password": "StrongPassword2026!",
    "full_name": "Inspector Vikram Singh",
    "role": "supervisor"
  }
  ```
- **Response `201 Created`:** User object without password hash.

#### `GET /api/auth/me`
- **Description:** Returns the profile and permissions of the currently authenticated token bearer.

---

### 2.2 Cameras & Multi-Camera Topology (`/api/cameras`)

#### `GET /api/cameras`
- **Description:** Lists all deployed optical and thermal border cameras.
- **Query Parameters:** `is_active` (bool), `sensor_type` (`OPTICAL`, `THERMAL_LWIR`, `ANPR`), `location` (string).
- **Response `200 OK`:**
  ```json
  [
    {
      "camera_id": "CAM-01",
      "name": "Approach Road North",
      "rtsp_url": "rtsp://127.0.0.1:8554/cam01",
      "location": "BOP-Ranidanga-N1",
      "latitude": 26.6854,
      "longitude": 88.3211,
      "sensor_type": "OPTICAL_4K",
      "edge_node_id": "EDGE-NODE-ALPHA-01",
      "is_active": true
    },
    {
      "camera_id": "CAM-03",
      "name": "Thermal Fence Line West",
      "rtsp_url": "rtsp://127.0.0.1:8554/cam03",
      "location": "BOP-Ranidanga-W3",
      "latitude": 26.6861,
      "longitude": 88.3195,
      "sensor_type": "THERMAL_LWIR",
      "edge_node_id": "EDGE-NODE-ALPHA-01",
      "is_active": true
    }
  ]
  ```

#### `POST /api/cameras`
- **Description:** Registers a new optical or thermal sensor into the border surveillance grid.

#### `GET /api/cameras/{id}/status`
- **Description:** Returns live hardware and ingestion telemetry (FPS, jitter, packet loss, hardware temp).
- **Response `200 OK`:**
  ```json
  {
    "camera_id": "CAM-01",
    "fps": 24.64,
    "jitter_ms": 0.61,
    "packet_loss_pct": 0.0,
    "status": "ONLINE",
    "cpu_temp_c": 48.2,
    "last_heartbeat": "2026-09-06T10:45:00Z"
  }
  ```

#### `POST /api/cameras/topology/predict-handoff`
- **Description:** Calculates the predictive trajectory corridor and ETA window for a target moving between non-overlapping camera FOVs.
- **Request Body:**
  ```json
  {
    "source_camera_id": "CAM-01",
    "track_id": 104,
    "heading_degrees": 185.0,
    "velocity_mps": 2.4
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "source_camera_id": "CAM-01",
    "track_id": 104,
    "predicted_next_cameras": [
      {
        "target_camera_id": "CAM-03",
        "transition_probability": 0.78,
        "distance_meters": 120.0,
        "eta_seconds": 50.0,
        "eta_window_start": "2026-09-06T10:45:35Z",
        "eta_window_end": "2026-09-06T10:46:05Z",
        "tactical_corridor": "West Treeline Infiltration Route"
      }
    ]
  }
  ```

---

### 2.3 Polygonal Zones & Curfew Rules (`/api/zones`)

#### `GET /api/zones`
- **Description:** Retrieves all virtual polygonal tripwires and monitoring zones.
- **Response `200 OK`:**
  ```json
  [
    {
      "zone_id": "ZONE-RESTRICTED-01",
      "camera_id": "CAM-03",
      "name": "Zero-Line Perimeter Fence",
      "zone_type": "RED_RESTRICTED",
      "polygon_coords": [[0.1, 0.2], [0.9, 0.2], [0.9, 0.8], [0.1, 0.8]],
      "dwell_threshold_sec": 0,
      "curfew_active": true
    }
  ]
  ```

#### `POST /api/zones`
- **Description:** Creates an arbitrary $N$-sided polygonal security zone with normalized `[0.0, 1.0]` coordinates.

---

### 2.4 Events & Edge Ingestion (`/api/events`)

#### `GET /api/events`
- **Description:** Queries discrete atomic detection and behavioral events with pagination and filters.
- **Query Parameters:** `camera_id`, `severity`, `start_time`, `end_time`, `limit`, `offset`.

#### `POST /api/events`
- **Description:** Ingestion endpoint for edge nodes to synchronize batched detection events.
- **Request Body:**
  ```json
  {
    "node_id": "EDGE-NODE-ALPHA-01",
    "batch_size": 2,
    "events": [
      {
        "event_id": "EVT-20260906-001",
        "camera_id": "CAM-03",
        "zone_id": "ZONE-RESTRICTED-01",
        "event_type": "PERIMETER_BREACH",
        "risk_score": 95.0,
        "severity": "CRITICAL",
        "timestamp": "2026-09-06T10:45:10Z",
        "metadata": {"inward_heading": true, "velocity_mps": 2.1}
      }
    ]
  }
  ```

---

### 2.5 Incident Fusion & Evidence Management (`/api/incidents`)

#### `GET /api/incidents`
- **Description:** Lists all multi-event fused incident records.
- **Response `200 OK`:**
  ```json
  [
    {
      "incident_id": "INC-20260905-001",
      "status": "OPEN",
      "severity": "CRITICAL",
      "primary_camera_id": "CAM-03",
      "start_time": "2026-09-06T10:42:00Z",
      "correlated_event_count": 3,
      "summary": "Coordinated approach vehicle drop-off and restricted fence line breach",
      "evidence_package_path": "/storage/evidence/INC-20260905-001.zip"
    }
  ]
  ```

#### `PUT /api/incidents/{id}/status`
- **Description:** Updates operational incident status (`OPEN`, `ACKNOWLEDGED`, `INVESTIGATING`, `ESCALATED`, `RESOLVED`, `FALSE_ALARM`).

#### `GET /api/incidents/{id}/evidence`
- **Description:** Streams the downloadable forensic evidence ZIP bundle (contains tactical HUD snapshot, bounding box JSON, and signed SHA-256 manifest).

---

### 2.6 Real-Time Alerts (`/api/alerts`)

#### `GET /api/alerts`
- **Description:** Returns active, unacknowledged tactical alerts for command room monitors.

#### `POST /api/alerts/{id}/ack`
- **Description:** Acknowledges an active alert, stopping acoustic sirens and recording operator action in the immutable audit trail.
- **Request Body:**
  ```json
  {
    "operator_notes": "QRT Unit 2 dispatched to Milepost 44 for physical interdiction."
  }
  ```

---

### 2.7 ANPR & Vehicle Intelligence (`/api/anpr`)

#### `GET /api/anpr/logs`
- **Description:** Returns captured license plates with state code parsing and confidence scores.
- **Query Parameters:** `state_code` (e.g., `DL`, `PB`, `JK`, `UP`), `is_hotlisted` (bool).

#### `POST /api/anpr/watchlist`
- **Description:** Flags a vehicle registration plate in the national hotlist (e.g., stolen vehicle, arms smuggler).

---

### 2.8 Facial Recognition & Biometric Governance (`/api/faces`)

#### `GET /api/faces/sightings`
- **Description:** Returns facial sighting detections with cosine similarity scores against watchlists.

#### `POST /api/faces/sightings/{id}/verify`
- **Description:** **Mandatory DPDP Act 2023 Human-in-the-Loop Gateway.** An operator explicitly confirms or rejects an automated facial match before biometric intelligence is committed.
- **Request Body:**
  ```json
  {
    "is_confirmed": true,
    "officer_badge_id": "SSB-78942",
    "verification_notes": "Visual match confirmed against suspect photo in NCB dossier."
  }
  ```

---

### 2.9 Unified Search & Discovery (`/api/search`)

#### `GET /api/search/unified`
- **Description:** Full-text multi-entity search across vehicle plates, suspect names, camera identifiers, and incident descriptions.
- **Query Parameters:** `q` (search term), `time_from`, `time_to`.

---

### 2.10 Immutable Audit Trail & Cryptographic Verification (`/api/audit`)

#### `GET /api/audit/logs`
- **Description:** Returns chronological audit records with previous and current SHA-256 block hashes.

#### `GET /api/audit/verify-chain`
- **Description:** **Mathematical verification of entire audit chain integrity.** Traverses all entries from the genesis block, recalculates SHA-256 digests, and reports whether any record has been modified or deleted.
- **Response `200 OK`:**
  ```json
  {
    "status": "VERIFIED_INTEGRITY",
    "total_records_audited": 1420,
    "genesis_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "terminal_hash": "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
    "chain_broken": false,
    "tamper_detected": false
  }
  ```

---

### 2.11 Platform Health & Diagnostics (`/api/health`)

#### `GET /api/health`
- **Description:** High-speed liveness and readiness probe for container orchestrators.

#### `GET /api/health/metrics`
- **Description:** Operational telemetry (CPU load, memory allocation, GPU utilization, disk free space, inference pipeline queue depth).

---

### 2.12 SIH 2026 Grand Finale Pitch Runner (`/api/demo`)

#### `POST /api/demo/run-scenario`
- **Description:** Executes the automated 8-step live pitch scenario simulating an approach vehicle, suspicious loitering, thermal perimeter breach, explainable risk escalation, and QRT dispatch.
- **Response `200 OK`:** Detailed step-by-step incident state progression.

---

## 3. Real-Time WebSocket Channels

### 3.1 Alert Notification Channel: `ws://127.0.0.1:8000/ws/alerts`
- **Purpose:** Sub-millisecond push of critical breach alerts directly to command room screens and QRT mobile tablets.
- **Message Payload:**
  ```json
  {
    "type": "PERIMETER_BREACH_ALERT",
    "incident_id": "INC-20260905-001",
    "camera_id": "CAM-03",
    "zone_name": "Zero-Line Perimeter Fence",
    "severity": "CRITICAL",
    "risk_score": 95,
    "timestamp": "2026-09-06T10:45:12Z",
    "snapshot_url": "http://127.0.0.1:8000/storage/snapshots/alert_104_CAM03.jpg",
    "explainable_card": {
      "restricted_zone_breach": 30,
      "nighttime_context": 15,
      "inward_heading_vector": 20,
      "watchlist_vehicle_match": 30
    }
  }
  ```

### 3.2 System Telemetry Channel: `ws://127.0.0.1:8000/ws/telemetry`
- **Purpose:** 1 Hz continuous operational stream delivering live camera FPS, edge buffer depth, and hardware temperatures.

---

## 4. Verification & Testing with cURL

### 4.1 Login & Retrieve Bearer Token
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=AdminSecurePassword2026!"
```

### 4.2 Query Active Border Cameras
```bash
curl -X GET "http://127.0.0.1:8000/api/cameras" \
     -H "Authorization: Bearer <YOUR_TOKEN>"
```

### 4.3 Verify Cryptographic Audit Chain Integrity
```bash
curl -X GET "http://127.0.0.1:8000/api/audit/verify-chain" \
     -H "Authorization: Bearer <YOUR_TOKEN>"
```

### 4.4 Trigger SIH Live Demo Pitch Scenario
```bash
curl -X POST "http://127.0.0.1:8000/api/demo/run-scenario" \
     -H "Authorization: Bearer <YOUR_TOKEN>"
```
