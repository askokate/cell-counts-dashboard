SHELL := /usr/bin/bash
.ONESHELL:

ENV_NAME := cell-counts-dashboard
BACKEND_DIR := backend
FRONTEND_DIR := frontend
DB_PATH := backend/data/app.db
CSV_PATH := data/cell-count.csv

define ACTIVATE
eval "$$(micromamba shell hook --shell bash)" && micromamba activate $(ENV_NAME)
endef

.PHONY: help
help:
	@echo "Targets:"
	@echo "  make env-create       Create micromamba env from backend/environment.yml"
	@echo "  make backend-install  Install/upgrade backend deps (pip -r requirements.txt)"
	@echo "  make load-db          Build SQLite DB from CSV"
	@echo "  make backend-dev      Run FastAPI locally (port 8000)"
	@echo "  make test             Run pytest"
	@echo "  make frontend-install Install frontend deps"
	@echo "  make frontend-dev     Run Vite dev server (port 5173)"

.PHONY: env-create
env-create:
	cd $(BACKEND_DIR)
	eval "$$(micromamba shell hook --shell bash)"
	# Create env if it doesn't exist; do not fail if it already exists
	micromamba env create -n $(ENV_NAME) -f environment.yml || true
	$(MAKE) backend-install

.PHONY: backend-install
backend-install:
	cd $(BACKEND_DIR)
	$(ACTIVATE)
	python -m pip install -U pip
	python -m pip install -r requirements.txt

.PHONY: load-db
load-db:
	cd $(BACKEND_DIR)
	$(ACTIVATE)
	python -m backend.app.load_db --csv ../$(CSV_PATH) --db ../$(DB_PATH) --replace

.PHONY: backend-dev
backend-dev:
	cd $(BACKEND_DIR)
	$(ACTIVATE)
	./start.sh

.PHONY: test
test:
	cd $(BACKEND_DIR)
	$(ACTIVATE)
	pytest -v

.PHONY: frontend-install
frontend-install:
	cd $(FRONTEND_DIR)
	npm install

.PHONY: frontend-dev
frontend-dev:
	cd $(FRONTEND_DIR)
	npm run dev -- --host 0.0.0.0 --port 5173