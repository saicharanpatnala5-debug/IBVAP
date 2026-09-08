"""
IBVAP - Unified Seed Runner
Executes tactical SQL seed scripts into the database.
"""
import os
import sys
import sqlite3

def run_all_seeds(db_path: str, seeds_dir: str):
    print(f"Running tactical seeds on database: {db_path}")
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    sql_files = sorted([f for f in os.listdir(seeds_dir) if f.endswith(".sql")])
    for f in sql_files:
        print(f"Applying seed: {f} ...")
        script_path = os.path.join(seeds_dir, f)
        with open(script_path, "r", encoding="utf-8") as sf:
            script_sql = sf.read()
        cursor.executescript(script_sql)
        print(f"  [OK] Successfully applied {f}")

    conn.commit()
    conn.close()
    print("All tactical seeds applied successfully!")

if __name__ == "__main__":
    db = os.environ.get("DATABASE_PATH", r"C:\Users\SAI CHARAN\OneDrive\Desktop\IBVAP\backend\storage\ibvap.db")
    sdir = os.path.dirname(os.path.abspath(__file__))
    run_all_seeds(db, sdir)
