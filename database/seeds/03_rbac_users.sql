-- Seed 03: Pre-Configured RBAC Tactical Users (PBKDF2 Password: AdminSecurePassword2026!)
INSERT OR REPLACE INTO users (username, hashed_password, full_name, role, is_active)
VALUES 
('admin', '1b2a75908235e2ba6be8e4544d935aa0$600000$ba25e368ff6663f73df0169225c56e29787d55998a1be5296ca8ef621f3d8a9f', 'SSB Force Commander (Admin)', 'admin', 1),
('inspector_sharma', '1b2a75908235e2ba6be8e4544d935aa0$600000$ba25e368ff6663f73df0169225c56e29787d55998a1be5296ca8ef621f3d8a9f', 'Inspector Rajesh Sharma', 'supervisor', 1),
('operator_singh', '1b2a75908235e2ba6be8e4544d935aa0$600000$ba25e368ff6663f73df0169225c56e29787d55998a1be5296ca8ef621f3d8a9f', 'Constable Gurpreet Singh', 'cctv_operator', 1),
('qrt_lead_kumar', '1b2a75908235e2ba6be8e4544d935aa0$600000$ba25e368ff6663f73df0169225c56e29787d55998a1be5296ca8ef621f3d8a9f', 'Sub-Inspector Amit Kumar (QRT)', 'field_response', 1),
('auditor_verma', '1b2a75908235e2ba6be8e4544d935aa0$600000$ba25e368ff6663f73df0169225c56e29787d55998a1be5296ca8ef621f3d8a9f', 'Director Neha Verma (MHA Auditor)', 'auditor', 1);
