#!/usr/bin/env bash
# Cluster Readiness and End-to-End Health Probe
set -euo pipefail

TARGET="${1:-http://localhost}"
echo "Probing IBVAP Health at: $TARGET..."

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$TARGET/api/health" || echo "000")
if [ "$HTTP_STATUS" = "200" ]; then
    echo "  [OK] Backend Health Status: 200 OK"
else
    echo "  [WARN] Backend returned status: $HTTP_STATUS"
fi
