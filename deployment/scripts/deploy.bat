@echo off
REM =========================================================================
REM IBVAP - One-Click Production Cluster Deployment (Windows CMD)
REM =========================================================================
echo ========================================================================
echo   IBVAP - TACTICAL CLUSTER DEPLOYER (WINDOWS)
echo ========================================================================

cd /d "%~dp0\..\docker"
echo [1/3] Building & Starting Docker Compose Production Cluster...
docker compose -f docker-compose.prod.yml up -d --build

echo [2/3] Waiting for services to initialize...
timeout /t 5 /nobreak >nul

echo [3/3] Deployment complete! Access via http://localhost/docs
pause
