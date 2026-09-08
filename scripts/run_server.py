"""
IBVAP - Server Launcher
Runs Uvicorn server on port 8000 with hot reloading.
"""
import uvicorn
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    print("=" * 60)
    print("  IBVAP - Intelligent Border Video Analytics Platform")
    print("  Smart India Hackathon (SIH 2026) | Problem Statement: SIH26187")
    print("  Ministry of Home Affairs / SSB, Police-II Division")
    print("=" * 60)
    print("Starting API Server at http://127.0.0.1:8000 ...")
    print("Interactive Documentation: http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
