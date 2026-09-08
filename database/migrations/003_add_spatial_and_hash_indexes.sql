-- Migration 003: Performance Indexes & Operational Views
CREATE INDEX IF NOT EXISTS idx_cameras_location ON cameras(location);
CREATE INDEX IF NOT EXISTS idx_zones_camera ON zones(camera_id);
CREATE INDEX IF NOT EXISTS idx_detections_time ON detections(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_time ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_alerts_ack ON alerts(is_acknowledged);
CREATE INDEX IF NOT EXISTS idx_vehicle_plates_plate ON vehicle_plates(plate_number);
CREATE INDEX IF NOT EXISTS idx_audit_current_hash ON audit_logs(current_hash);
CREATE INDEX IF NOT EXISTS idx_topology_pair ON camera_topology_edges(source_camera_id, target_camera_id);

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
