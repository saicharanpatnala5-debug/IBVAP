-- Seed 05: Fused Incident Scenario & Cryptographic Audit Chain
INSERT OR REPLACE INTO incidents (incident_id, status, severity, primary_camera_id, start_time, end_time, correlated_event_count, summary, evidence_package_path)
VALUES 
('INC-20260905-001', 'OPEN', 'CRITICAL', 'CAM-03', CURRENT_TIMESTAMP, NULL, 3, 
 'Coordinated multi-stage incursion: approach vehicle drop-off at CAM-01, suspicious loitering, and zero-line perimeter breach detected on FLIR thermal CAM-03.',
 '/storage/evidence/INC-20260905-001.zip');

INSERT OR REPLACE INTO alerts (alert_id, incident_id, severity, summary, is_acknowledged)
VALUES 
('ALT-20260905-001', 'INC-20260905-001', 'CRITICAL', 'Zero-Line Restricted Zone Breach detected on CAM-03 (Risk Score: 125)', 0),
('ALT-20260905-002', 'INC-20260905-001', 'HIGH', 'Blacklisted Vehicle DL01AB1234 identified approaching checkpoint on CAM-02', 1);

INSERT OR REPLACE INTO audit_logs (user_id, action, entity_type, entity_id, prev_hash, current_hash, details)
VALUES 
('SYSTEM_GENESIS', 'SYSTEM_INITIALIZATION', 'DATABASE', 'SCHEMA_V1',
 '0000000000000000000000000000000000000000000000000000000000000000',
 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
 '{"status": "BOOTSTRAP_COMPLETE", "sector": "BOP-Ranidanga"}'),
('admin', 'ALERT_ESCALATION', 'INCIDENT', 'INC-20260905-001',
 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
 '7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069',
 '{"escalation_level": "RED_CODE", "qrt_dispatched": "UNIT_2"}');
