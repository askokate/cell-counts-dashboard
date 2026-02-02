SHELL := /usr/bin/env bash
.ONESHELL:
.DEFAULT_GOAL := help

# -------- Config --------
ENV_NAME := cell-counts-dashboard
BACKEND_DIR := backend
FRONTEND_DIR := frontend
CSV_PATH := data/cell-count.csv
DB_PATH := backend/data/app.db

ACTIVATE := eval "$$(micromamba shell hook --shell bash)" && micromamba activate $(ENV_NAME)

# -------- Help --------
.PHONY: help
help:
	@echo ""
	@echo "Available targets:"
	@echo "  make backend-dev     Create env (if needed), install deps, run API on :8000"
	@echo "  make frontend-dev    Install npm deps (if needed), run UI on :5173"
	@echo "  make load-db         Rebuild SQLite DB from CSV"
	@echo "  make test            Run backend tests"
	@echo ""

# -------- Guards --------
.PHONY: check-micromamba
check-micromamba:
	command -v micromamba >/dev/null 2>&1 || { \
		echo "❌ micromamba not found."; \
		echo "   Run in GitHub Codespaces or install with:"; \
		echo "   curl -Ls https://micro.mamba.pm/install.sh | bash"; \
		exit 1; \
	}

# -------- Backend --------
.PHONY: env-create
env-create: check-micromamba
	cd $(BACKEND_DIR)
	eval "$$(micromamba shell hook --shell bash)"
	micromamba env create -n $(ENV_NAME) -f environment.yml || true

.PHONY: backend-install
backend-install: env-create
	cd $(BACKEND_DIR)
	$(ACTIVATE)
	python -m pip install -U pip
	python -m pip install -r requirements.txt

.PHONY: backend-dev
backend-dev: backend-install
	cd $(BACKEND_DIR)
	$(ACTIVATE)
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

.PHONY: load-db
load-db: backend-install
	cd $(BACKEND_DIR)
	$(ACTIVATE)
	python -m app.load_db --csv ../$(CSV_PATH) --db data/app.db --replace

.PHONY: test
test: backend-install
	cd $(BACKEND_DIR)
	$(ACTIVATE)
	pytest -v

# -------- Frontend --------
.PHONY: frontend-install
frontend-install:
	cd $(FRONTEND_DIR)
	npm ci

.PHONY: frontend-dev
frontend-dev: frontend-install
	cd $(FRONTEND_DIR)
	npm run dev -- --host 0.0.0.0 --port 5173