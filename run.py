"""
IBVAP - Top-level Server Launcher
Launches backend from project root.
"""
import uvicorn
import os
import sys

# Ensure backend directory and root directory are in python path
root_path = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(root_path, "backend")
os.chdir(backend_path)
sys.path.insert(0, root_path)
sys.path.insert(0, backend_path)

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IBVAP Border Analytics Platform Launcher")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--reload", action="store_true", default=False, help="Enable auto-reload")
    args = parser.parse_args()

    print("=" * 60)
    print("  IBVAP - Intelligent Border Video Analytics Platform")
    print("  Smart India Hackathon (SIH 2026)")
    print("=" * 60)
    print(f"Starting server at http://127.0.0.1:{args.port} ...")
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload, app_dir=backend_path)
