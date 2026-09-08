"""
IBVAP - Versioned Migration Runner
Discovers and applies versioned SQL migrations idempotently.
"""
import os
import sqlite3
import re
from typing import List

class MigrationRunner:
    def __init__(self, db_path: str, migrations_dir: str):
        self.db_path = db_path
        self.migrations_dir = migrations_dir

    def init_migration_table(self, conn: sqlite3.Connection):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version VARCHAR(100) NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

    def get_applied_migrations(self, conn: sqlite3.Connection) -> List[str]:
        cursor = conn.execute("SELECT version FROM schema_migrations ORDER BY id ASC")
        return [row[0] for row in cursor.fetchall()]

    def run_migrations(self) -> int:
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        self.init_migration_table(conn)
        applied = set(self.get_applied_migrations(conn))

        files = sorted([f for f in os.listdir(self.migrations_dir) if f.endswith(".sql")])
        new_applied = 0

        for f in files:
            if f not in applied:
                print(f"Applying migration: {f} ...")
                script_path = os.path.join(self.migrations_dir, f)
                with open(script_path, "r", encoding="utf-8") as sf:
                    sql_script = sf.read()
                
                cursor = conn.cursor()
                cursor.executescript(sql_script)
                cursor.execute("INSERT INTO schema_migrations (version) VALUES (?)", (f,))
                conn.commit()
                new_applied += 1
                print(f"  [OK] Successfully applied {f}")

        conn.close()
        return new_applied

if __name__ == "__main__":
    db = os.environ.get("DATABASE_PATH", r"C:\Users\SAI CHARAN\OneDrive\Desktop\IBVAP\backend\storage\ibvap.db")
    mdir = os.path.dirname(os.path.abspath(__file__))
    runner = MigrationRunner(db, mdir)
    count = runner.run_migrations()
    print(f"Migrations complete. {count} new migration(s) applied.")
