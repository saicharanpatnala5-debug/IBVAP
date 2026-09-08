#!/usr/bin/env bash
# =========================================================================
# IBVAP - Automated Tactical Production Deployer (Linux / macOS / WSL)
# =========================================================================
set -euo pipefail

echo "========================================================================"
echo "  IBVAP - TACTICAL PRODUCTION CLUSTER DEPLOYMENT"
echo "  Standard: Smart India Hackathon (SIH 2026) | SIH26187"
echo "========================================================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 1. Prerequisite verification
echo "[1/5] Checking tactical dependencies..."
command -v docker >/dev/null 2>&1 || { echo "ERROR: Docker required."; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo "ERROR: docker compose required."; exit 1; }

# 2. Generate local certificates if missing
if [ ! -f "$ROOT_DIR/deployment/nginx/certs/ibvap.crt" ]; then
    echo "[2/5] Generating tactical SSL certificates..."
    bash "$ROOT_DIR/deployment/nginx/certs/generate_self_signed.sh"
else
    echo "[2/5] SSL Certificates already active."
fi

# 3. Build & Orchestrate Containers
echo "[3/5] Launching multi-container production cluster..."
cd "$ROOT_DIR/deployment/docker"
docker compose -f docker-compose.prod.yml up -d --build

# 4. Health Probe
echo "[4/5] Executing cluster readiness probe..."
sleep 5
bash "$ROOT_DIR/deployment/scripts/health_check.sh"

echo "[5/5] DEPLOYMENT COMPLETE!"
echo "  - Command Web UI:      http://localhost"
echo "  - Central API & Docs:  http://localhost/docs"
echo "  - Grafana Telemetry:   http://localhost:3000 (commandant / TacticalCommand2026!)"
echo "  - Prometheus Scrapes:  http://localhost:9090"
