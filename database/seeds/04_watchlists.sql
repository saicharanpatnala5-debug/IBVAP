-- Seed 04: Watchlists (Stolen Vehicles & Suspect Persons of Interest)
INSERT OR REPLACE INTO watchlists (entity_type, identifier, threat_level, reason)
VALUES 
('VEHICLE', 'DL01AB1234', 'HIGH', 'Stolen Mahindra Bolero linked to cross-border arms syndicate'),
('VEHICLE', 'PB02XY9999', 'CRITICAL', 'Repeated contraband transport courier across Indo-Nepal border'),
('VEHICLE', 'HR26BK4567', 'MEDIUM', 'Unregistered commercial vehicle evading checkpoint taxation'),
('PERSON', 'SUSPECT-ID-78942', 'CRITICAL', 'Wanted in connection with fake currency (FICN) smuggling ring'),
('PERSON', 'SUSPECT-ID-99411', 'HIGH', 'Suspected cross-border human trafficking courier');
