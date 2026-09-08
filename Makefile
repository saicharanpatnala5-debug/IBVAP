.PHONY: help install test test-coverage seed run run-edge docker-up docker-down verify-dataset airgap clean

help:
	@echo "========================================================================"
	@echo "  IBVAP Tactical Operations & Automation Runner (SIH 2026)"
	@echo "========================================================================"
	@echo "  make install         - Install all Python, AI, and backend dependencies"
	@echo "  make test            - Execute all 42 automated pytest suites"
	@echo "  make test-coverage   - Run tests with code coverage metrics"
	@echo "  make seed            - Seed tactical border cameras, zones, and users"
	@echo "  make run             - Launch Central Command FastAPI server"
	@echo "  make run-edge        - Launch autonomous forward edge node"
	@echo "  make verify-dataset  - Verify integrity of multi-spectral dataset & videos"
	@echo "  make docker-up       - Launch production docker-compose cluster"
	@echo "  make docker-down     - Terminate docker-compose cluster"
	@echo "  make airgap          - Bundle encrypted offline air-gapped field package"
	@echo "  make clean           - Clear temporary caches, pyc files, and test logs"

install:
	pip install -r requirements.txt

test:
	pytest backend/tests/ -v

test-coverage:
	pytest backend/tests/ --cov=backend/app --cov-report=term-missing

seed:
	python scripts/seed_db.py

run:
	python run.py

run-edge:
	python -m edge.main --duration 60

verify-dataset:
	python datasets/scripts/verify_dataset.py

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

airgap:
	bash deployment/scripts/airgap_package.sh

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
