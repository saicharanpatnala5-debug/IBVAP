#!/usr/bin/env bash
# Bundles entire IBVAP platform into an encrypted/compressed air-gapped tarball
set -euo pipefail

PACKAGE_NAME="ibvap_airgap_$(date +%Y%m%d).tar.gz"
echo "Packaging IBVAP into Air-Gapped Deployment Bundle: $PACKAGE_NAME..."

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

tar --exclude='.git' --exclude='__pycache__' --exclude='.pytest_cache' \
    --exclude='*.pyc' -czvf "$PACKAGE_NAME" \
    backend ai video edge configs database deployment scripts README.md

echo "Air-gap package created: $PACKAGE_NAME ($(du -h "$PACKAGE_NAME" | cut -f1))"
