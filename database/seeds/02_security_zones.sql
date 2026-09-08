-- Seed 02: Ray-Casting Virtual Zones
INSERT OR REPLACE INTO zones (zone_id, camera_id, name, zone_type, polygon_coords, is_active, dwell_threshold_sec, curfew_active)
VALUES 
('ZONE-RESTRICTED-01', 'CAM-03', 'Zero-Line Border Perimeter', 'RED_RESTRICTED', '[[0.05, 0.15], [0.95, 0.15], [0.95, 0.85], [0.05, 0.85]]', 1, 0, 1),
('ZONE-BUFFER-01', 'CAM-01', 'Northern Buffer Approach Zone', 'YELLOW_MONITORING', '[[0.10, 0.20], [0.90, 0.20], [0.90, 0.80], [0.10, 0.80]]', 1, 15, 0),
('ZONE-CHECKPOINT-01', 'CAM-02', 'Authorized Transit Gate Lane', 'GREEN_NORMAL', '[[0.25, 0.30], [0.75, 0.30], [0.75, 0.70], [0.25, 0.70]]', 1, 60, 0),
('ZONE-DEPOT-01', 'CAM-07', 'Strategic Ammunition Depot', 'RED_RESTRICTED', '[[0.08, 0.10], [0.92, 0.10], [0.92, 0.90], [0.08, 0.90]]', 1, 0, 1);
