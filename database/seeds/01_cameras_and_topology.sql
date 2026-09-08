-- Seed 01: Cameras & Topology Graph
INSERT OR REPLACE INTO cameras (camera_id, name, rtsp_url, location, latitude, longitude, sensor_type, edge_node_id, is_active)
VALUES 
('CAM-01', 'Approach Road North', 'rtsp://127.0.0.1:8554/cam01', 'BOP-Ranidanga-N1', 26.6854, 88.3211, 'OPTICAL_4K', 'EDGE-NODE-ALPHA-01', 1),
('CAM-02', 'Checkpoint North Gate ANPR', 'rtsp://127.0.0.1:8554/cam02', 'BOP-Ranidanga-Gate', 26.6858, 88.3204, 'ANPR_CAMERA', 'EDGE-NODE-ALPHA-01', 1),
('CAM-03', 'Thermal Fence Line West', 'rtsp://127.0.0.1:8554/cam03', 'BOP-Ranidanga-W3', 26.6861, 88.3195, 'THERMAL_LWIR', 'EDGE-NODE-ALPHA-01', 1),
('CAM-04', 'Tower 360 Starlight PTZ', 'rtsp://127.0.0.1:8554/cam04', 'BOP-Ranidanga-Tower', 26.6850, 88.3220, 'STARLIGHT_PTZ', 'EDGE-NODE-ALPHA-02', 1),
('CAM-05', 'South Transit Corridor', 'rtsp://127.0.0.1:8554/cam05', 'BOP-Ranidanga-S2', 26.6842, 88.3225, 'OPTICAL_4K', 'EDGE-NODE-ALPHA-02', 1),
('CAM-07', 'Inner Strategic Depot', 'rtsp://127.0.0.1:8554/cam07', 'BOP-Ranidanga-Depot', 26.6835, 88.3230, 'THERMAL_LWIR', 'EDGE-NODE-ALPHA-02', 1);

INSERT OR REPLACE INTO camera_health (camera_id, fps, jitter_ms, packet_loss_pct, status, cpu_temp_c, storage_free_gb)
VALUES 
('CAM-01', 24.8, 0.61, 0.0, 'ONLINE', 47.5, 155.2),
('CAM-02', 25.0, 0.52, 0.0, 'ONLINE', 48.0, 155.2),
('CAM-03', 25.0, 0.74, 0.0, 'ONLINE', 46.2, 155.2),
('CAM-04', 24.5, 0.85, 0.0, 'ONLINE', 49.1, 142.8),
('CAM-05', 25.0, 0.60, 0.0, 'ONLINE', 45.9, 142.8),
('CAM-07', 25.0, 0.65, 0.0, 'ONLINE', 46.5, 142.8);

INSERT OR REPLACE INTO camera_topology_edges (source_camera_id, target_camera_id, transition_probability, min_transit_time_sec, max_transit_time_sec, distance_meters, tactical_corridor)
VALUES 
('CAM-01', 'CAM-02', 0.85, 15.0, 45.0, 80.0, 'North Infiltration Approach'),
('CAM-01', 'CAM-03', 0.78, 30.0, 75.0, 120.0, 'West Treeline Bypass'),
('CAM-02', 'CAM-04', 0.65, 40.0, 90.0, 150.0, 'Main Checkpoint Transit'),
('CAM-03', 'CAM-05', 0.72, 45.0, 100.0, 180.0, 'Perimeter Fence Flank'),
('CAM-05', 'CAM-07', 0.90, 20.0, 50.0, 95.0, 'Depot Access Route');
