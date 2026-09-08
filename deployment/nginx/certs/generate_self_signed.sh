#!/usr/bin/env bash
# Generates 4096-bit RSA mTLS tactical certificates for offline border post encryption
set -euo pipefail

CERT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$CERT_DIR"

echo "Generating Tactical 4096-bit Self-Signed SSL Certificate for IBVAP..."
openssl req -x509 -nodes -days 730 -newkey rsa:4096 \
    -keyout "$CERT_DIR/ibvap.key" \
    -out "$CERT_DIR/ibvap.crt" \
    -subj "/C=IN/ST=New Delhi/L=MHA/O=Sashastra Seema Bal/OU=Police-II/CN=ibvap.bop-alpha.ssb.gov.in"

chmod 600 "$CERT_DIR/ibvap.key"
chmod 644 "$CERT_DIR/ibvap.crt"
echo "Certificates generated successfully: $CERT_DIR/ibvap.crt"
