# ==============================================================================
# IBVAP: Autonomous Environment Setup & Provisioning Subsystem (PowerShell)
# Standard: Smart India Hackathon (SIH 2026) | Problem Statement: SIH26187
# Ministry of Home Affairs / Sashastra Seema Bal (SSB), Police-II Division
# ==============================================================================

Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host "  IBVAP - Autonomous Environment Provisioning Sequence" -ForegroundColor Cyan
Write-Host "  Smart India Hackathon 2026 | Ministry of Home Affairs / SSB" -ForegroundColor Cyan
Write-Host "==========================================================================" -ForegroundColor Cyan

$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

Write-Host "[1/5] Initializing storage directory structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "storage/snapshots", "storage/clips", "storage/buffer", "storage/evidence", "storage/logs", "ai/detection/models" | Out-Null

Write-Host "[2/5] Downloading / Verifying AI model repository..." -ForegroundColor Yellow
python scripts/download_models.py --synthetic

Write-Host "[3/5] Seeding tactical border outpost database (BOP Alpha Sector B)..." -ForegroundColor Yellow
python scripts/seed_db.py

Write-Host "[4/5] Executing high-performance subsystem benchmark..." -ForegroundColor Yellow
python scripts/benchmark.py --quick

Write-Host "[5/5] Running platform self-test..." -ForegroundColor Yellow
Push-Location backend
python -m pytest tests/ -q
Pop-Location

Write-Host "==========================================================================" -ForegroundColor Green
Write-Host "  [OK] IBVAP PLATFORM SETUP COMPLETE AND READY FOR OPERATION!" -ForegroundColor Green
Write-Host "  To launch the server: python run.py" -ForegroundColor Green
Write-Host "  Swagger UI:           http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "==========================================================================" -ForegroundColor Green
