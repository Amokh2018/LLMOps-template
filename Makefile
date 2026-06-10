.PHONY: help setup install lint type-check test format clean docker-build docker-push deploy gcp-auth vector-index

# Variables
PYTHON := python3
PYTHON_VERSION := 3.11
VENV := venv
SERVICES := api ingestion
REGISTRY := us-docker.pkg.dev
PROJECT_ID ?= $(shell gcloud config get-value project)
REGION ?= us-central1

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)LLMOps Template - Make Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup Commands:$(NC)"
	@echo "  make setup              Install everything for local development"
	@echo "  make install            Install Python dependencies"
	@echo "  make venv               Create virtual environment"
	@echo ""
	@echo "$(YELLOW)Development Commands:$(NC)"
	@echo "  make api                Run API service locally"
	@echo "  make ingest             Run ingestion pipeline"
	@echo "  make docker-up          Start services with Docker Compose"
	@echo "  make docker-down        Stop Docker Compose services"
	@echo ""
	@echo "$(YELLOW)Code Quality:$(NC)"
	@echo "  make lint               Run linting (ruff)"
	@echo "  make format             Format code with ruff"
	@echo "  make type-check         Run type checking (mypy)"
	@echo "  make test               Run tests"
	@echo "  make quality            Run lint + type-check + test"
	@echo ""
	@echo "$(YELLOW)Docker Commands:$(NC)"
	@echo "  make docker-build       Build all Docker images"
	@echo "  make docker-build-api   Build API Docker image"
	@echo "  make docker-build-ingest Build ingestion Docker image"
	@echo "  make docker-push        Push images to Artifact Registry"
	@echo ""
	@echo "$(YELLOW)GCP Commands:$(NC)"
	@echo "  make gcp-auth           Authenticate with GCP"
	@echo "  make gcp-init           Initialize GCP infrastructure"
	@echo "  make gcp-deploy         Deploy to Cloud Run"
	@echo "  make gcp-logs           View API service logs"
	@echo "  make vector-index       Create Vector Search index"
	@echo ""
	@echo "$(YELLOW)Utility:$(NC)"
	@echo "  make clean              Remove build artifacts and cache"
	@echo "  make config             Copy environment template"
	@echo "  make check              Run all checks"
	@echo ""

# Setup & Installation
setup: venv install config ## Setup complete development environment
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo "  Run 'make api' to start the API service"

venv: ## Create Python virtual environment
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV); \
		echo "$(GREEN)✓ Virtual environment created$(NC)"; \
	else \
		echo "Virtual environment already exists"; \
	fi

install: ## Install all dependencies
	@echo "Installing dependencies..."
	@. $(VENV)/bin/activate && pip install --upgrade pip
	@. $(VENV)/bin/activate && pip install -r services/api/requirements.txt
	@. $(VENV)/bin/activate && pip install -r services/ingestion/requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

config: ## Copy environment template
	@if [ ! -f ".env" ]; then \
		cp config/dev.env.example .env; \
		echo "$(GREEN)✓ Created .env file$(NC)"; \
		echo "  Edit .env with your GCP project ID and other values"; \
	else \
		echo ".env already exists"; \
	fi

# Development
api: ## Run API service locally
	@echo "Starting API service..."
	@. $(VENV)/bin/activate && cd services/api && python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000

ingest: ## Run ingestion pipeline
	@echo "Starting ingestion pipeline..."
	@. $(VENV)/bin/activate && cd services/ingestion && python main.py

docker-up: ## Start services with Docker Compose
	@docker-compose up

docker-down: ## Stop Docker Compose services
	@docker-compose down

# Code Quality
lint: ## Run linting checks
	@echo "Running linting..."
	@. $(VENV)/bin/activate && ruff check services/api services/ingestion
	@echo "$(GREEN)✓ Linting passed$(NC)"

format: ## Format code with ruff
	@echo "Formatting code..."
	@. $(VENV)/bin/activate && ruff format services/api services/ingestion
	@echo "$(GREEN)✓ Code formatted$(NC)"

type-check: ## Run type checking
	@echo "Running type checks..."
	@. $(VENV)/bin/activate && mypy services/api services/ingestion --ignore-missing-imports
	@echo "$(GREEN)✓ Type checking passed$(NC)"

test: ## Run tests
	@echo "Running tests..."
	@. $(VENV)/bin/activate && pytest services/api/tests -v
	@echo "$(GREEN)✓ Tests passed$(NC)"

quality: lint type-check test ## Run all quality checks
	@echo "$(GREEN)✓ All quality checks passed$(NC)"

# Docker
docker-build: ## Build all Docker images
	@echo "Building Docker images..."
	@docker build -t api-service:latest services/api
	@docker build -t ingestion-service:latest services/ingestion
	@echo "$(GREEN)✓ Docker images built$(NC)"

docker-build-api: ## Build API Docker image
	@echo "Building API Docker image..."
	@docker build -t api-service:latest services/api
	@echo "$(GREEN)✓ API Docker image built$(NC)"

docker-build-ingest: ## Build ingestion Docker image
	@echo "Building ingestion Docker image..."
	@docker build -t ingestion-service:latest services/ingestion
	@echo "$(GREEN)✓ Ingestion Docker image built$(NC)"

docker-push: docker-build ## Build and push images to Artifact Registry
	@echo "Pushing images to Artifact Registry..."
	@docker tag api-service:latest $(REGISTRY)/$(PROJECT_ID)/rag-services/api-service:latest
	@docker tag ingestion-service:latest $(REGISTRY)/$(PROJECT_ID)/rag-services/ingestion-service:latest
	@docker push $(REGISTRY)/$(PROJECT_ID)/rag-services/api-service:latest
	@docker push $(REGISTRY)/$(PROJECT_ID)/rag-services/ingestion-service:latest
	@echo "$(GREEN)✓ Images pushed to Artifact Registry$(NC)"

# GCP Commands
gcp-auth: ## Authenticate with GCP
	@echo "Authenticating with GCP..."
	@gcloud auth application-default login
	@echo "$(GREEN)✓ GCP authentication complete$(NC)"

gcp-init: ## Initialize GCP infrastructure with Terraform
	@echo "Initializing GCP infrastructure..."
	@cd infra/terraform && \
	terraform init && \
	terraform plan -var="project_id=$(PROJECT_ID)" -var="gcs_bucket_name=$(PROJECT_ID)-documents" && \
	echo "Review the plan above and run: make gcp-apply"

gcp-apply: ## Apply Terraform configuration
	@echo "Applying Terraform configuration..."
	@cd infra/terraform && \
	terraform apply -var="project_id=$(PROJECT_ID)" -var="gcs_bucket_name=$(PROJECT_ID)-documents"
	@echo "$(GREEN)✓ Infrastructure deployed$(NC)"

gcp-deploy: docker-push ## Deploy to Cloud Run
	@echo "Deploying to Cloud Run..."
	@gcloud run deploy api-service \
		--image $(REGISTRY)/$(PROJECT_ID)/rag-services/api-service:latest \
		--platform managed \
		--region $(REGION) \
		--allow-unauthenticated \
		--set-env-vars GCP_PROJECT_ID=$(PROJECT_ID),VERTEX_AI_LOCATION=$(REGION)
	@echo "$(GREEN)✓ API deployed to Cloud Run$(NC)"

gcp-logs: ## View API service logs
	@gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=api-service" \
		--limit 50 \
		--format json

gcp-url: ## Get API service URL
	@gcloud run services describe api-service --region $(REGION) --format 'value(status.url)'

vector-index: ## Create Vector Search index (manual steps)
	@echo "$(YELLOW)Vector Search Index Setup$(NC)"
	@echo ""
	@echo "To create a Vector Search index:"
	@echo "1. Go to: https://console.cloud.google.com/vertex-ai/vector-search"
	@echo "2. Click 'Create Index'"
	@echo "3. Configure:"
	@echo "   - Name: rag-documents"
	@echo "   - Embedding Dimensions: 768"
	@echo "   - Distance Measure: COSINE_DISTANCE"
	@echo "4. Copy the endpoint URL"
	@echo "5. Update .env with VECTOR_STORE_INDEX_ID and VECTOR_STORE_ENDPOINT"
	@echo ""

# Testing & Verification
check: quality ## Run all checks
	@echo "$(GREEN)✓ All checks passed$(NC)"

check-gcp: ## Check GCP authentication and project
	@echo "Checking GCP configuration..."
	@gcloud config list --format="value(core.project)"
	@gcloud auth list
	@echo "$(GREEN)✓ GCP ready$(NC)"

test-api: ## Test API locally
	@echo "Testing API..."
	@curl -s http://localhost:8000/health | jq .
	@echo "$(GREEN)✓ API is healthy$(NC)"

# Cleanup
clean: ## Remove build artifacts and cache
	@echo "Cleaning up..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name *.egg-info -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name .DS_Store -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-docker: ## Remove Docker images
	@echo "Removing Docker images..."
	@docker rmi api-service:latest ingestion-service:latest 2>/dev/null || true
	@echo "$(GREEN)✓ Docker images removed$(NC)"

# Quick reference
.DEFAULT_GOAL := help
