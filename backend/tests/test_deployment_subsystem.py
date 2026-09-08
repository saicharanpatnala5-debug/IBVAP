"""
IBVAP - Deployment Subsystem Automated Test Suite
Validates Dockerfiles, Compose specs, Nginx reverse proxy configs, Prometheus alert rules, and deployment scripts.
"""
import os
import json
import pytest
import yaml

DEPLOYMENT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "deployment"))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def test_docker_files_and_compose_configs():
    docker_dir = os.path.join(DEPLOYMENT_ROOT, "docker")
    assert os.path.isdir(docker_dir)
    
    # Check Dockerfiles
    for df in ["Dockerfile.backend", "Dockerfile.frontend", "Dockerfile.edge", ".dockerignore"]:
        p = os.path.join(docker_dir, df)
        assert os.path.exists(p), f"Missing docker file: {df}"
        assert os.path.getsize(p) > 20

    # Validate docker-compose.prod.yml
    prod_compose = os.path.join(docker_dir, "docker-compose.prod.yml")
    with open(prod_compose, "r", encoding="utf-8") as f:
        prod_data = yaml.safe_load(f)
        assert "services" in prod_data
        for svc in ["backend", "postgres", "redis", "nginx", "prometheus", "grafana"]:
            assert svc in prod_data["services"]

    # Validate docker-compose.airgap.yml
    airgap_compose = os.path.join(docker_dir, "docker-compose.airgap.yml")
    with open(airgap_compose, "r", encoding="utf-8") as f:
        airgap_data = yaml.safe_load(f)
        assert "services" in airgap_data
        assert "edge_node" in airgap_data["services"]
        assert "local_gateway" in airgap_data["services"]

def test_nginx_configs():
    nginx_dir = os.path.join(DEPLOYMENT_ROOT, "nginx")
    assert os.path.isdir(nginx_dir)
    
    # 1. Main config
    main_conf = os.path.join(nginx_dir, "nginx.conf")
    assert os.path.exists(main_conf)
    with open(main_conf, "r", encoding="utf-8") as f:
        content = f.read()
        assert "worker_processes" in content
        assert "limit_req_zone" in content

    # 2. Virtual host config
    vhost_conf = os.path.join(nginx_dir, "conf.d", "ibvap.conf")
    assert os.path.exists(vhost_conf)
    with open(vhost_conf, "r", encoding="utf-8") as f:
        content = f.read()
        assert "upstream backend_upstream" in content
        assert "location /ws/" in content
        assert "Upgrade $http_upgrade" in content
        assert "location /storage/" in content

    # 3. Security headers config
    sec_conf = os.path.join(nginx_dir, "conf.d", "security-headers.conf")
    assert os.path.exists(sec_conf)
    with open(sec_conf, "r", encoding="utf-8") as f:
        content = f.read()
        assert "X-Frame-Options" in content
        assert "Content-Security-Policy" in content

def test_monitoring_configs():
    mon_dir = os.path.join(DEPLOYMENT_ROOT, "monitoring")
    assert os.path.isdir(mon_dir)
    
    # 1. Prometheus config
    prom_yaml = os.path.join(mon_dir, "prometheus", "prometheus.yml")
    assert os.path.exists(prom_yaml)
    with open(prom_yaml, "r", encoding="utf-8") as f:
        prom = yaml.safe_load(f)
        assert "scrape_configs" in prom
        job_names = [j["job_name"] for j in prom["scrape_configs"]]
        assert "ibvap_backend" in job_names
        assert "ibvap_edge_fleet" in job_names

    # 2. Alert rules
    alert_yaml = os.path.join(mon_dir, "prometheus", "alert_rules.yml")
    assert os.path.exists(alert_yaml)
    with open(alert_yaml, "r", encoding="utf-8") as f:
        alerts = yaml.safe_load(f)
        rule_names = [r["alert"] for g in alerts["groups"] for r in g["rules"]]
        assert "PerimeterBreachSurge" in rule_names
        assert "CameraStreamLinkLoss" in rule_names

    # 3. Grafana dashboards
    dash_path = os.path.join(mon_dir, "grafana", "dashboards", "ibvap_command_overview.json")
    assert os.path.exists(dash_path)
    with open(dash_path, "r", encoding="utf-8") as f:
        dash = json.load(f)
        assert "panels" in dash
        assert len(dash["panels"]) >= 4

    # 4. Alertmanager
    am_yaml = os.path.join(mon_dir, "alertmanager", "config.yml")
    assert os.path.exists(am_yaml)

def test_deployment_scripts_and_systemd():
    scripts_dir = os.path.join(DEPLOYMENT_ROOT, "scripts")
    for s in ["deploy.sh", "deploy.bat", "deploy.ps1", "airgap_package.sh", "health_check.sh", "rollback.sh"]:
        p = os.path.join(scripts_dir, s)
        assert os.path.exists(p), f"Missing script: {s}"
        assert os.path.getsize(p) > 20

    systemd_dir = os.path.join(DEPLOYMENT_ROOT, "systemd")
    for svc in ["ibvap-backend.service", "ibvap-edge.service"]:
        p = os.path.join(systemd_dir, svc)
        assert os.path.exists(p), f"Missing service unit: {svc}"
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
            assert "[Unit]" in content
            assert "[Service]" in content
            assert "[Install]" in content

def test_root_scaffold_files():
    # Makefile
    mf = os.path.join(PROJECT_ROOT, "Makefile")
    assert os.path.exists(mf)
    with open(mf, "r", encoding="utf-8") as f:
        c = f.read()
        for target in ["help:", "test:", "seed:", "run:", "docker-up:"]:
            assert target in c

    # LICENSE
    lic = os.path.join(PROJECT_ROOT, "LICENSE")
    assert os.path.exists(lic)
    with open(lic, "r", encoding="utf-8") as f:
        c = f.read()
        assert "Sashastra Seema Bal" in c
        assert "DPDP" in c

    # .gitignore
    gi = os.path.join(PROJECT_ROOT, ".gitignore")
    assert os.path.exists(gi)
