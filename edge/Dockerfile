# ==============================================================================
# IBVAP: Intelligent Border Video Analytics Platform - Edge Node Runtime
# Architecture: Multi-Arch (x86_64 / ARM64 NVIDIA Jetson Orin/Xavier)
# Standard: Smart India Hackathon (SIH 2026) | Problem Statement: SIH26187
# Ministry of Home Affairs / Sashastra Seema Bal (SSB), Police-II Division
# ==============================================================================

FROM python:3.11-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    EDGE_HOME=/app

# Install rugged edge OS dependencies (FFmpeg for RTSP, SQLite3, OpenCV runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    sqlite3 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR ${EDGE_HOME}

# Create tactical non-root user
RUN groupadd -g 1001 ibvap && \
    useradd -u 1001 -g ibvap -s /bin/bash -m ibvap

# Install Edge Python dependencies
COPY edge/requirements.txt ${EDGE_HOME}/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy platform source tree
COPY . ${EDGE_HOME}

# Create local buffer and evidence directories with appropriate permissions
RUN mkdir -p ${EDGE_HOME}/storage/edge_buffer \
             ${EDGE_HOME}/storage/edge_evidence \
             ${EDGE_HOME}/storage/logs && \
    chown -R ibvap:ibvap ${EDGE_HOME}

USER ibvap

# Healthcheck validating local Edge Daemon telemetry
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "from edge.sync.network_monitor import network_monitor; print(network_monitor.get_status()['backhaul_connected'])" || exit 1

EXPOSE 8080

ENTRYPOINT ["python", "-m", "edge.main"]
CMD ["--mode", "DAEMON"]
