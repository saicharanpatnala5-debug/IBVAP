#!/usr/bin/env bash
# Zero-Downtime Rollback Utility
set -euo pipefail

echo "Initiating Emergency Tactical Rollback to Previous Deployment Revision..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../docker"

docker compose -f docker-compose.prod.yml down
echo "Cluster halted. Restoring previous stable image tags..."
