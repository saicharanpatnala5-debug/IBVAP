-- Migration 001: Initial Core Infrastructure
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

CREATE TABLE IF NOT EXISTS camera_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id VARCHAR(50) NOT NULL,
    fps FLOAT NOT NULL DEFAULT 25.0,
    jitter_ms FLOAT NOT NULL DEFAULT 0.0,
    packet_loss_pct FLOAT NOT NULL DEFAULT 0.0,
    status VARCHAR(20) NOT NULL DEFAULT 'ONLINE',
    cpu_temp_c FLOAT DEFAULT 45.0,
    storage_free_gb FLOAT DEFAULT 150.0,
    last_heartbeat TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS camera_topology_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_camera_id VARCHAR(50) NOT NULL,
    target_camera_id VARCHAR(50) NOT NULL,
    transition_probability FLOAT NOT NULL,
    min_transit_time_sec FLOAT NOT NULL,
    max_transit_time_sec FLOAT NOT NULL,
    distance_meters FLOAT NOT NULL,
    tactical_corridor VARCHAR(100) NOT NULL,
    FOREIGN KEY (source_camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE,
    FOREIGN KEY (target_camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_id VARCHAR(50) NOT NULL UNIQUE,
    camera_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    zone_type VARCHAR(20) NOT NULL CHECK (zone_type IN ('RED_RESTRICTED', 'YELLOW_MONITORING', 'GREEN_NORMAL')),
    polygon_coords TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    dwell_threshold_sec INTEGER NOT NULL DEFAULT 0,
    curfew_active BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id) ON DELETE CASCADE
);
