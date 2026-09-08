# IBVAP: Defense Deployment & Operations Manual

[![Stack](https://img.shields.io/badge/Stack-Docker%20Compose%20%7C%20Nginx%20%7C%20Prometheus%20%7C%20Grafana-blue.svg)](#architecture)
[![Environment](https://img.shields.io/badge/Environment-Air--Gapped%20BOP%20%7C%20Central%20HQ-darkgreen.svg)](#air-gapped-field-operations)
[![Compliance](https://img.shields.io/badge/Security-mTLS%20%7C%20DPDP%20Act%202023-brightgreen.svg)](#security--compliance)

Comprehensive operational deployment suite for the **Intelligent Border Video Analytics Platform (IBVAP)**, standardizing deployments across high-availability central command posts and offline, ruggedized forward border outposts (BOP Alpha).

---

## 1. Directory Layout

```text
deployment/
├── README.md                                  # Operations & deployment guide
│
├── docker/                                    # Containerization manifests
│   ├── Dockerfile.backend                     # Multi-stage production FastAPI server
│   ├── Dockerfile.frontend                    # Multi-stage Alpine Nginx dashboard
│   ├── Dockerfile.edge                        # Lightweight ARM64/Jetson edge runtime
│   ├── docker-compose.prod.yml                # Central HQ production cluster
│   ├── docker-compose.airgap.yml              # Offline forward border outpost stack
│   └── .dockerignore
│
├── nginx/                                     # Reverse proxy & SSL gateway
│   ├── nginx.conf                             # High-concurrency proxy with HTTP/2
│   ├── conf.d/
│   │   ├── ibvap.conf                         # Routing, WebSocket upgrades, storage mounts
│   │   └── security-headers.conf              # Military-grade security headers (HSTS, CSP)
│   └── certs/
│       └── generate_self_signed.sh            # 4096-bit mTLS certificate generator
│
├── monitoring/                                # Observability & Telemetry
│   ├── prometheus/
│   │   ├── prometheus.yml                     # Central scrape configs (5s interval)
│   │   └── alert_rules.yml                    # Perimeter breach & camera loss rules
│   ├── grafana/
│   │   ├── dashboards/                        # Pre-configured tactical dashboards
│   │   └── provisioning/                      # Auto-provisioned datasources
│   └── alertmanager/
│       └── config.yml                         # Alert escalation router
│
├── scripts/                                   # Operational scripts
│   ├── deploy.sh / deploy.bat / deploy.ps1    # Idempotent cross-platform deployers
│   ├── airgap_package.sh                      # Encrypted air-gap bundle packager
│   ├── health_check.sh                        # Cluster readiness probe
│   └── rollback.sh                            # Zero-downtime rollback utility
│
└── systemd/                                   # Linux host service units
    ├── ibvap-backend.service                  # Central backend service unit
    └── ibvap-edge.service                     # Edge node daemon service unit
```

---

## 2. Quickstart Deployment

### Option A: Central Command Post (Docker Compose)

```bash
cd "C:\Users\SAI CHARAN\OneDrive\Desktop\IBVAP\deployment\scripts"

# On Windows:
deploy.bat
# or PowerShell:
.\deploy.ps1

# On Linux / macOS:
bash deploy.sh
```

- **Web Dashboard**: [http://localhost](http://localhost)
- **Interactive Swagger API**: [http://localhost/docs](http://localhost/docs)
- **Grafana Defense Telemetry**: [http://localhost:3000](http://localhost:3000) (`commandant` / `TacticalCommand2026!`)
- **Prometheus Metrics**: [http://localhost:9090](http://localhost:9090)

---

### Option B: Offline Air-Gapped Border Outpost (BOP Alpha)

In sensitive border zones with zero internet or cloud connectivity:

```bash
# 1. Package air-gapped bundle at HQ
bash deployment/scripts/airgap_package.sh

# 2. Transfer package via encrypted military drive to BOP Alpha
# 3. Launch isolated offline edge stack
cd deployment/docker
docker compose -f docker-compose.airgap.yml up -d
```

---

## 3. Host Systemd Installation (Linux / Jetson)

For bare-metal or NVIDIA Jetson deployment without Docker:

```bash
sudo cp deployment/systemd/ibvap-backend.service /etc/systemd/system/
sudo cp deployment/systemd/ibvap-edge.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ibvap-backend.service
sudo systemctl enable --now ibvap-edge.service
```
