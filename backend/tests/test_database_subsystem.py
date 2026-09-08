"""
IBVAP - Database Subsystem Test Suite
Tests schema.sql DDL validity, versioned migrations, modular seed execution,
analytical SQL views, and ER diagram image integrity.
"""
import os
import sys
import sqlite3
import tempfile
from PIL import Image
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.migrations.runner import MigrationRunner
from database.seeds.seed_runner import run_all_seeds

SCHEMA_SQL_PATH = os.path.join(PROJECT_ROOT, "database", "schema.sql")
MIGRATIONS_DIR = os.path.join(PROJECT_ROOT, "database", "migrations")
SEEDS_DIR = os.path.join(PROJECT_ROOT, "database", "seeds")
ER_DIAGRAM_PATH = os.path.join(PROJECT_ROOT, "database", "er-diagram.png")

def test_schema_sql_ddl():
    """Verifies that schema.sql executes cleanly and creates all 14 tables + 3 views."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_db = os.path.join(tmp_dir, "test_schema.db")
        conn = sqlite3.connect(test_db)
        
        with open(SCHEMA_SQL_PATH, "r", encoding="utf-8") as f:
            ddl = f.read()
        
        conn.executescript(ddl)
        
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = set(row[0] for row in cursor.fetchall())
        
        expected_tables = {
            "users", "cameras", "camera_health", "camera_topology_edges",
            "zones", "detections", "tracks", "events", "incidents", "alerts",
            "vehicle_plates", "face_sightings", "watchlists", "audit_logs"
        }
        for table in expected_tables:
            assert table in tables, f"Expected table {table} not found in schema.sql"
            
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        views = set(row[0] for row in cursor.fetchall())
        expected_views = {
            "v_active_incidents_summary",
            "v_camera_health_overview",
            "v_anpr_hotlist_matches"
        }
        for view in expected_views:
            assert view in views, f"Expected view {view} not found in schema.sql"
            
        conn.close()

def test_migration_runner_idempotency():
    """Tests applying versioned migrations sequentially and verifies idempotence."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_db = os.path.join(tmp_dir, "test_mig.db")
        runner = MigrationRunner(test_db, MIGRATIONS_DIR)
        
        # First execution applies all migrations
        applied_count = runner.run_migrations()
        assert applied_count == 3
        
        # Second execution applies 0 migrations
        reapplied_count = runner.run_migrations()
        assert reapplied_count == 0

def test_seeds_and_views():
    """Applies migrations and seeds, then verifies row counts and analytical views."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_db = os.path.join(tmp_dir, "test_seeds.db")
        runner = MigrationRunner(test_db, MIGRATIONS_DIR)
        runner.run_migrations()
        
        run_all_seeds(test_db, SEEDS_DIR)
        
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM cameras")
        assert cursor.fetchone()[0] >= 6
        
        cursor.execute("SELECT COUNT(*) FROM camera_topology_edges")
        assert cursor.fetchone()[0] >= 5
        
        cursor.execute("SELECT COUNT(*) FROM zones")
        assert cursor.fetchone()[0] >= 4
        
        cursor.execute("SELECT COUNT(*) FROM users")
        assert cursor.fetchone()[0] >= 5
        
        cursor.execute("SELECT COUNT(*) FROM watchlists")
        assert cursor.fetchone()[0] >= 5
        
        cursor.execute("SELECT COUNT(*) FROM incidents")
        assert cursor.fetchone()[0] >= 1
        
        cursor.execute("SELECT COUNT(*) FROM alerts")
        assert cursor.fetchone()[0] >= 2
        
        cursor.execute("SELECT COUNT(*) FROM audit_logs")
        assert cursor.fetchone()[0] >= 2
        
        # Verify View: v_active_incidents_summary
        cursor.execute("SELECT incident_id, camera_name, alert_count FROM v_active_incidents_summary")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "INC-20260905-001"
        assert "Thermal" in row[1]
        assert row[2] >= 1
        
        # Verify View: v_camera_health_overview
        cursor.execute("SELECT COUNT(*) FROM v_camera_health_overview WHERE status = 'ONLINE'")
        assert cursor.fetchone()[0] >= 6
        
        conn.close()

def test_er_diagram_image():
    """Verifies that er-diagram.png exists, has high resolution and valid size."""
    assert os.path.exists(ER_DIAGRAM_PATH), f"ER diagram not found at {ER_DIAGRAM_PATH}"
    file_size = os.path.getsize(ER_DIAGRAM_PATH)
    assert file_size > 500_000, f"Expected ER diagram > 500KB, got {file_size} bytes"
    
    with Image.open(ER_DIAGRAM_PATH) as img:
        assert img.format == "PNG"
        assert img.size[0] >= 6000
        assert img.size[1] >= 3500
