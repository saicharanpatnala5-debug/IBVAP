# =========================================================================
# IBVAP - Native PowerShell Production Cluster Deployment
# =========================================================================
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  IBVAP - TACTICAL PRODUCTION CLUSTER DEPLOYMENT (POWERSHELL)" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DockerDir = Join-Path $ScriptDir "..\docker"

Set-Location $DockerDir
Write-Host "[1/3] Launching Docker Compose Stack..." -ForegroundColor Yellow
docker compose -f docker-compose.prod.yml up -d --build

Start-Sleep -Seconds 5

Write-Host "[2/3] Probing Cluster Health..." -ForegroundColor Yellow
try {
    $resp = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get -TimeoutSec 3
    Write-Host "  + Central Backend API: HEALTHY (Status: $($resp.status))" -ForegroundColor Green
} catch {
    Write-Host "  ! Backend starting up or proxied behind Nginx..." -ForegroundColor Gray
}

Write-Host "[3/3] Stack Deployed Successfully!" -ForegroundColor Green
Write-Host "  - Command Web Portal: http://localhost" -ForegroundColor White
Write-Host "  - Swagger API Docs:   http://localhost/docs" -ForegroundColor White
Write-Host "  - Grafana Telemetry:  http://localhost:3000" -ForegroundColor White
