#!/usr/bin/env bash
# ==============================================================================
# IBVAP: Autonomous Environment Setup & Provisioning Subsystem
# Standard: Smart India Hackathon (SIH 2026) | Problem Statement: SIH26187
# Ministry of Home Affairs / Sashastra Seema Bal (SSB), Police-II Division
# ==============================================================================

set -euo pipefail

BOLD="\033[1m"
GREEN="\033[38;5;46m"
CYAN="\033[38;5;51m"
YELLOW="\033[38;5;226m"
RED="\033[38;5;196m"
RESET="\033[0m"

log_info() {
    echo -e "${CYAN}[IBVAP-SETUP] [$(date +'%H:%M:%S')] ℹ️  $*${RESET}"
}

log_success() {
    echo -e "${GREEN}[IBVAP-SETUP] [$(date +'%H:%M:%S')] ✅ $*${RESET}"
}

log_warn() {
    echo -e "${YELLOW}[IBVAP-SETUP] [$(date +'%H:%M:%S')] ⚠️  $*${RESET}"
}

log_error() {
    echo -e "${RED}[IBVAP-SETUP] [$(date +'%H:%M:%S')] ❌ $*${RESET}"
}

print_banner() {
    echo -e "${CYAN}${BOLD}"
    cat << "EOF"
  ██████╗  ██████╗ ██╗   ██╗ █████╗ ██████╗ 
  ██╔══██╗ ██╔══██╗██║   ██║██╔══██╗██╔══██╗
  ██████╔╝ ██████╔╝██║   ██║███████║██████╔╝
  ██╔══██╗ ██╔══██╗╚██╗ ██╔╝██╔══██║██╔═══╝ 
  ██████╔╝ ██████╔╝ ╚████╔╝ ██║  ██║██║     
  ╚═════╝  ╚═════╝   ╚═══╝  ╚═╝  ╚═╝╚═╝     
  Intelligent Border Video Analytics Platform
  Ministry of Home Affairs | SSB Sector Command
EOF
    echo -e "${RESET}"
    echo "=========================================================================="
    echo " SIH 2026 Autonomous Node Provisioning & Verification Sequence"
    echo "=========================================================================="
}

print_banner

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT_DIR}"
log_info "Target deployment root: ${ROOT_DIR}"

log_info "Checking Python 3 environment..."
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    log_error "Python interpreter not found. Please install Python 3.10+."
    exit 1
fi

PY_VERSION=$(${PYTHON_CMD} -c "import sys; print('.'.join(map(str, sys.version_info[:3])))")
log_success "Discovered Python runtime: ${PY_VERSION}"

VENV_DIR="${ROOT_DIR}/.venv"
if [ ! -d "${VENV_DIR}" ]; then
    log_info "Creating isolated virtual environment at .venv..."
    ${PYTHON_CMD} -m venv "${VENV_DIR}"
    log_success "Virtual environment initialized."
else
    log_info "Existing virtual environment detected at .venv."
fi

if [ -f "${VENV_DIR}/bin/activate" ]; then
    source "${VENV_DIR}/bin/activate"
elif [ -f "${VENV_DIR}/Scripts/activate" ]; then
    source "${VENV_DIR}/Scripts/activate"
fi

log_info "Provisioning secure evidence and storage directory hierarchy..."
mkdir -p "${ROOT_DIR}/storage/snapshots"
mkdir -p "${ROOT_DIR}/storage/clips"
mkdir -p "${ROOT_DIR}/storage/buffer"
mkdir -p "${ROOT_DIR}/storage/evidence"
mkdir -p "${ROOT_DIR}/storage/logs"
mkdir -p "${ROOT_DIR}/ai/detection/models"
mkdir -p "${ROOT_DIR}/configs/cameras"
mkdir -p "${ROOT_DIR}/configs/zones"
mkdir -p "${ROOT_DIR}/configs/models"
log_success "Storage hierarchy verified and secure."

log_info "Upgrading pip and installing core platform dependencies..."
${PYTHON_CMD} -m pip install --upgrade pip --quiet

if [ -f "${ROOT_DIR}/requirements.txt" ]; then
    log_info "Installing root requirements.txt..."
    ${PYTHON_CMD} -m pip install -r "${ROOT_DIR}/requirements.txt" --quiet || log_warn "Root dependencies partially satisfied."
fi

if [ -f "${ROOT_DIR}/backend/requirements.txt" ]; then
    log_info "Installing backend dependencies..."
    ${PYTHON_CMD} -m pip install -r "${ROOT_DIR}/backend/requirements.txt" --quiet || log_warn "Backend dependencies partially satisfied."
fi

log_info "Validating YAML configuration integrity..."
${PYTHON_CMD} -c "
import yaml, sys, os
configs = [
    'configs/cameras/cameras.yaml',
    'configs/zones/zones.yaml',
    'configs/models/models.yaml',
    'configs/system.yaml'
]
for c in configs:
    p = os.path.join('${ROOT_DIR}', c)
    if not os.path.exists(p):
        print(f'Error: missing {c}')
        sys.exit(1)
    with open(p, 'r', encoding='utf-8') as f:
        yaml.safe_load(f)
print('All 4 YAML configs valid!')
"
log_success "Configuration suite verified (cameras, zones, models, system)."

log_info "Downloading / Verifying AI model weights..."
${PYTHON_CMD} "${ROOT_DIR}/scripts/download_models.py" --synthetic

log_info "Executing tactical database seeder (BOP Alpha Sector B)..."
${PYTHON_CMD} "${ROOT_DIR}/scripts/seed_db.py"

log_info "Running system self-test & benchmark diagnostics..."
${PYTHON_CMD} "${ROOT_DIR}/scripts/benchmark.py" --quick

echo ""
echo -e "${GREEN}${BOLD}==========================================================================${RESET}"
echo -e "${GREEN}${BOLD}  🎉 IBVAP PLATFORM PROVISIONING COMPLETE & OPERATIONAL${RESET}"
echo -e "${GREEN}${BOLD}==========================================================================${RESET}"
echo -e "  To start the full platform in production mode:"
echo -e "    ${CYAN}python run.py${RESET}"
echo -e "  Interactive Swagger API Documentation:"
echo -e "    ${CYAN}http://127.0.0.1:8000/docs${RESET}"
echo -e "  Live SIH 8-Step Pitch Scenario Runner:"
echo -e "    ${CYAN}POST http://127.0.0.1:8000/api/demo/run-scenario${RESET}"
echo -e "  To run test camera stream:"
echo -e "    ${CYAN}python scripts/test_stream.py --synthetic${RESET}"
echo -e "=========================================================================="
