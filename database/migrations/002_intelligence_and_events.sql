-- Migration 002: Threat Intelligence, Detections, Incidents & Watchlists
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    detection_id VARCHAR(50) NOT NULL UNIQUE,
    camera_id VARCHAR(50) NOT NULL,
    class_name VARCHAR(50) NOT NULL,
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

CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id INTEGER NOT NULL,
    camera_id VARCHAR(50) NOT NULL,
    trajectory TEXT NOT NULL,
    velocity_mps FLOAT NOT NULL DEFAULT 0.0,
    heading_degrees FLOAT NOT NULL DEFAULT 0.0,
    dwell_time_sec FLOAT NOT NULL DEFAULT 0.0,
    is_inward BOOLEAN NOT NULL DEFAULT 0,
    first_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN',
    severity VARCHAR(20) NOT NULL,
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

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id VARCHAR(50) NOT NULL UNIQUE,
    camera_id VARCHAR(50) NOT NULL,
    zone_id VARCHAR(50),
    event_type VARCHAR(50) NOT NULL,
    risk_score FLOAT NOT NULL DEFAULT 0.0,
    severity VARCHAR(20) NOT NULL,
    metadata TEXT,
    incident_id VARCHAR(50),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE,
    FOREIGN KEY (zone_id) REFERENCES zones(zone_id) ON DELETE SET NULL,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id VARCHAR(50) NOT NULL UNIQUE,
    incident_id VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    summary VARCHAR(255) NOT NULL,
    is_acknowledged BOOLEAN NOT NULL DEFAULT 0,
    acknowledged_by VARCHAR(50),
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id) ON DELETE CASCADE,
    FOREIGN KEY (acknowledged_by) REFERENCES users(username) ON DELETE SET NULL
);

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

CREATE TABLE IF NOT EXISTS face_sightings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sighting_id VARCHAR(50) NOT NULL UNIQUE,
    camera_id VARCHAR(50) NOT NULL,
    person_name VARCHAR(100),
    similarity FLOAT NOT NULL,
    is_watchlist_match BOOLEAN NOT NULL DEFAULT 0,
    verified_by_human BOOLEAN NOT NULL DEFAULT 0,
    officer_notes TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    snapshot_path VARCHAR(255),
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS watchlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('PERSON', 'VEHICLE')),
    identifier VARCHAR(100) NOT NULL UNIQUE,
    threat_level VARCHAR(20) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    face_embedding TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(50),
    prev_hash VARCHAR(64) NOT NULL,
    current_hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);
