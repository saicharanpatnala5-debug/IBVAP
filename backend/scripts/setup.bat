@echo off
REM ==============================================================================
REM IBVAP: Autonomous Environment Setup & Provisioning Subsystem (Windows CMD)
REM Standard: Smart India Hackathon (SIH 2026) | Problem Statement: SIH26187
REM Ministry of Home Affairs / Sashastra Seema Bal (SSB), Police-II Division
REM ==============================================================================

echo ==========================================================================
echo   IBVAP - Autonomous Environment Provisioning Sequence
echo   Smart India Hackathon (SIH 2026) | Ministry of Home Affairs / SSB
echo ==========================================================================

cd /d "%~dp0\.."

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+ and add to PATH.
    pause
    exit /b 1
)

echo [1/5] Initializing storage directory structure...
if not exist "storage\snapshots" mkdir "storage\snapshots"
if not exist "storage\clips" mkdir "storage\clips"
if not exist "storage\buffer" mkdir "storage\buffer"
if not exist "storage\evidence" mkdir "storage\evidence"
if not exist "storage\logs" mkdir "storage\logs"
if not exist "ai\detection\models" mkdir "ai\detection\models"

echo [2/5] Downloading / Verifying AI model repository...
python scripts\download_models.py --synthetic

echo [3/5] Seeding tactical border outpost database (BOP Alpha Sector B)...
python scripts\seed_db.py

echo [4/5] Executing high-performance subsystem benchmark...
python scripts\benchmark.py --quick

echo [5/5] Running platform self-test...
cd backend
python -m pytest tests/ -q
cd ..

echo ==========================================================================
echo   [OK] IBVAP PLATFORM SETUP COMPLETE AND READY FOR OPERATION!
echo   To launch the server: python run.py
echo   Swagger UI:           http://127.0.0.1:8000/docs
echo ==========================================================================
pause
