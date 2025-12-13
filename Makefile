# =============================================================================
# SPDP - Makefile Operativo
# =============================================================================
# Variables
PROJECT_ID ?= $(shell grep PROJECT_ID .env | cut -d '=' -f2)
REGION ?= us-central1
REPO_NAME ?= spdp-repo
IMAGE_NAME ?= etl-runner
TAG ?= latest
ARTIFACT_URL = $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO_NAME)/$(IMAGE_NAME):$(TAG)

# Detectar python environment
PYTHON = .venv/bin/python
PIP = .venv/bin/pip

.PHONY: help setup run deploy maintenance

help:
	@echo "🛠️  SPDP COMANDOS DISPONIBLES"
	@echo "------------------------------"
	@echo "make setup       -> Instalar dependencias (venv)"
	@echo "make run         -> Ejecutar Pipeline ETL localmente"
	@echo "make status      -> Ver estado de watermarks"
	@echo "make deploy      -> Construir y subir imagen a Artifact Registry"
	@echo "make clean       -> Limpiar archivos temporales (__pycache__)"

setup:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt
	@echo "✅ Entorno listo. Usa 'source .venv/bin/activate'"

run:
	$(PYTHON) -m src.main

status:
	$(PYTHON) scripts/maintenance.py status

deploy:
	@echo "🚀 Desplegando a Google Artifact Registry..."
	gcloud builds submit --tag $(ARTIFACT_URL) .
	@echo "✅ Imagen subida: $(ARTIFACT_URL)"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
