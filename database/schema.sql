-- ====================================================================
-- IBVAP - INTELLIGENT BORDER VIDEO ANALYTICS PLATFORM
-- Complete Relational Database Schema DDL (PostgreSQL & SQLite Compatible)
-- Standard: Smart India Hackathon (SIH 2026) | Problem Statement: SIH26187
-- Ministry of Home Affairs / Sashastra Seema Bal (SSB), Police-II Division
-- ====================================================================

-- 1. USERS & ACCESS CONTROL TABLE (RBAC)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'supervisor', 'cctv_operator', 'field_response', 'auditor')),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. SENSOR & CAMERA INFRASTRUCTURE TABLE
CREATE TABLE IF NOT EXISTS cameras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    rtsp_url VARCHAR(255) NOT NULL,
    location VARCHAR(100) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    sensor_type VARCHAR(20) NOT NULL CHECK (sensor_type IN ('OPTICAL_4K', 'THERMAL_LWIR', 'ANPR_CAMERA', 'STARLIGHT_PTZ')),
    edge_node_id VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. CAMERA HEALTH & TELEMETRY MONITORING TABLE
CREATE TABLE IF NOT EXISTS camera_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id VARCHAR(50) NOT NULL,
    fps FLOAT NOT NULL DEFAULT 25.0,
    jitter_ms FLOAT NOT NULL DEFAULT 0.0,
    packet_loss_pct FLOAT NOT NULL DEFAULT 0.0,
    status VARCHAR(20) NOT NULL DEFAULT 'ONLINE' CHECK (status IN ('ONLINE', 'DEGRADED', 'OFFLINE', 'RECONNECTING')),
    cpu_temp_c FLOAT DEFAULT 45.0,
    storage_free_gb FLOAT DEFAULT 150.0,
    last_heartbeat TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE
);

-- 4. MULTI-CAMERA TOPOLOGY DIRECTED GRAPH EDGES
CREATE TABLE IF NOT EXISTS camera_topology_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_camera_id VARCHAR(50) NOT NULL,
    target_camera_id VARCHAR(50) NOT NULL,
    transition_probability FLOAT NOT NULL CHECK (transition_probability >= 0.0 AND transition_probability <= 1.0),
    min_transit_time_sec FLOAT NOT NULL,
    max_transit_time_sec FLOAT NOT NULL,
    distance_meters FLOAT NOT NULL,
    tactical_corridor VARCHAR(100) NOT NULL,
    FOREIGN KEY (source_camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE,
    FOREIGN KEY (target_camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE
);

-- 5. VIRTUAL POLYGONAL SECURITY ZONES & TRIPWIRES
CREATE TABLE IF NOT EXISTS zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_id VARCHAR(50) NOT NULL UNIQUE,
    camera_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    zone_type VARCHAR(20) NOT NULL CHECK (zone_type IN ('RED_RESTRICTED', 'YELLOW_MONITORING', 'GREEN_NORMAL')),
    polygon_coords TEXT NOT NULL, -- JSON array of normalized [x, y] coordinates
    is_active BOOLEAN NOT NULL DEFAULT 1,
    dwell_threshold_sec INTEGER NOT NULL DEFAULT 0,
    curfew_active BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE
);

-- 6. REAL-TIME DETECTIONS LOG
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    detection_id VARCHAR(50) NOT NULL UNIQUE,
    camera_id VARCHAR(50) NOT NULL,
    class_name VARCHAR(50) NOT NULL CHECK (class_name IN ('person', 'car', 'truck', 'motorcycle', 'bus', 'animal')),
    confidence FLOAT NOT NULL,
    bbox_x FLOAT NOT NULL,
    bbox_y FLOAT NOT NULL,
    bbox_w FLOAT NOT NULL,
    bbox_h FLOAT NOT NULL,
    is_thermal BOOLEAN NOT NULL DEFAULT 0,
    snapshot_path VARCHAR(255),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE
);

-- 7. MULTI-OBJECT TRAJECTORY TRACKS (8-D KALMAN)
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id INTEGER NOT NULL,
    camera_id VARCHAR(50) NOT NULL,
    trajectory TEXT NOT NULL, -- JSON list of centroid coordinates & timestamps
    velocity_mps FLOAT NOT NULL DEFAULT 0.0,
    heading_degrees FLOAT NOT NULL DEFAULT 0.0,
    dwell_time_sec FLOAT NOT NULL DEFAULT 0.0,
    is_inward BOOLEAN NOT NULL DEFAULT 0,
    first_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE
);

-- 8. BEHAVIORAL & PERIMETER BREACH EVENTS
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id VARCHAR(50) NOT NULL UNIQUE,
    camera_id VARCHAR(50) NOT NULL,
    zone_id VARCHAR(50),
    event_type VARCHAR(50) NOT NULL,
    risk_score FLOAT NOT NULL DEFAULT 0.0,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('NORMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    metadata TEXT, -- JSON attributes
    incident_id VARCHAR(50),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE,
    FOREIGN KEY (zone_id) REFERENCES zones(zone_id) ON DELETE SET NULL,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id) ON DELETE SET NULL
);

-- 9. FUSED STRATEGIC INCIDENTS DOSSIER
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'ACKNOWLEDGED', 'INVESTIGATING', 'ESCALATED', 'RESOLVED', 'FALSE_ALARM')),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    primary_camera_id VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    correlated_event_count INTEGER NOT NULL DEFAULT 1,
    summary TEXT NOT NULL,
    evidence_package_path VARCHAR(255),
    resolved_by_user VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (primary_camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by_user) REFERENCES users(username) ON DELETE SET NULL
);

-- 10. REAL-TIME TACTICAL ALERTS & QRT NOTIFICATIONS
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id VARCHAR(50) NOT NULL UNIQUE,
    incident_id VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    summary VARCHAR(255) NOT NULL,
    is_acknowledged BOOLEAN NOT NULL DEFAULT 0,
    acknowledged_by VARCHAR(50),
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id) ON DELETE CASCADE,
    FOREIGN KEY (acknowledged_by) REFERENCES users(username) ON DELETE SET NULL
);

-- 11. ANPR CAPTURED LICENSE PLATES
CREATE TABLE IF NOT EXISTS vehicle_plates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number VARCHAR(20) NOT NULL,
    camera_id VARCHAR(50) NOT NULL,
    state_code VARCHAR(5) NOT NULL,
    confidence FLOAT NOT NULL,
    is_hotlisted BOOLEAN NOT NULL DEFAULT 0,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    snapshot_path VARCHAR(255),
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE
);

-- 12. FACIAL RECOGNITION SIGHTINGS (DPDP GOVERNED)
CREATE TABLE IF NOT EXISTS face_sightings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sighting_id VARCHAR(50) NOT NULL UNIQUE,
    camera_id VARCHAR(50) NOT NULL,
    person_name VARCHAR(100),
    similarity FLOAT NOT NULL,
    is_watchlist_match BOOLEAN NOT NULL DEFAULT 0,
    verified_by_human BOOLEAN NOT NULL DEFAULT 0, -- Statutory DPDP Act 2023 requirement
    officer_notes TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    snapshot_path VARCHAR(255),
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE
);

-- 13. NATIONAL INTELLIGENCE WATCHLISTS
CREATE TABLE IF NOT EXISTS watchlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('PERSON', 'VEHICLE')),
    identifier VARCHAR(100) NOT NULL UNIQUE, -- Plate number or Suspect National ID
    threat_level VARCHAR(20) NOT NULL CHECK (threat_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    reason VARCHAR(255) NOT NULL,
    face_embedding TEXT, -- JSON 128-D vector (encrypted in production)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 14. CRYPTOGRAPHIC IMMUTABLE AUDIT TRAIL (SHA-256 HASH CHAIN)
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(50),
    prev_hash VARCHAR(64) NOT NULL,
    current_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details TEXT -- JSON payload of mutation
);

-- ====================================================================
-- PERFORMANCE INDEXES (OPTIMIZED FOR BORDER ANALYTICS WORKLOADS)
-- ====================================================================
CREATE INDEX IF NOT EXISTS idx_cameras_location ON cameras(location);
CREATE INDEX IF NOT EXISTS idx_zones_camera ON zones(camera_id);
CREATE INDEX IF NOT EXISTS idx_detections_time ON detections(timestamp);
CREATE INDEX IF NOT EXISTS idx_detections_cam_time ON detections(camera_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_tracks_camera ON tracks(camera_id);
CREATE INDEX IF NOT EXISTS idx_events_time ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_ack ON alerts(is_acknowledged);
CREATE INDEX IF NOT EXISTS idx_vehicle_plates_plate ON vehicle_plates(plate_number);
CREATE INDEX IF NOT EXISTS idx_vehicle_plates_hotlist ON vehicle_plates(is_hotlisted);
CREATE INDEX IF NOT EXISTS idx_face_sightings_match ON face_sightings(is_watchlist_match);
CREATE INDEX IF NOT EXISTS idx_audit_current_hash ON audit_logs(current_hash);
CREATE INDEX IF NOT EXISTS idx_topology_pair ON camera_topology_edges(source_camera_id, target_camera_id);

-- ====================================================================
-- ANALYTICAL VIEWS
-- ====================================================================

-- Active Incidents with Camera and Alert Counts
CREATE VIEW IF NOT EXISTS v_active_incidents_summary AS
SELECT 
    i.incident_id,
    i.status,
    i.severity,
    i.primary_camera_id,
    c.name AS camera_name,
    c.location AS camera_location,
    i.start_time,
    i.correlated_event_count,
    COUNT(a.id) AS alert_count,
    i.summary
FROM incidents i
JOIN cameras c ON i.primary_camera_id = c.camera_id
LEFT JOIN alerts a ON i.incident_id = a.incident_id
WHERE i.status IN ('OPEN', 'ACKNOWLEDGED', 'INVESTIGATING', 'ESCALATED')
GROUP BY i.incident_id;

-- Real-Time Camera Health Overview
CREATE VIEW IF NOT EXISTS v_camera_health_overview AS
SELECT 
    c.camera_id,
    c.name,
    c.sensor_type,
    c.location,
    h.status,
    h.fps,
    h.jitter_ms,
    h.packet_loss_pct,
    h.cpu_temp_c,
    h.last_heartbeat
FROM cameras c
LEFT JOIN camera_health h ON c.camera_id = h.camera_id;

-- Vehicle Hotlist Intercept Log
CREATE VIEW IF NOT EXISTS v_anpr_hotlist_matches AS
SELECT 
    vp.id,
    vp.plate_number,
    vp.state_code,
    vp.camera_id,
    c.name AS camera_name,
    vp.confidence,
    vp.timestamp,
    w.threat_level,
    w.reason AS hotlist_reason
FROM vehicle_plates vp
JOIN watchlists w ON vp.plate_number = w.identifier AND w.entity_type = 'VEHICLE'
JOIN cameras c ON vp.camera_id = c.camera_id
WHERE vp.is_hotlisted = 1;
