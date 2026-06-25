# ============================================================
# Makefile — AI WhatsApp Automation Platform
# ============================================================

.PHONY: help dev build test lint migrate seed docker-up docker-down clean

PYTHON := python3
PIP := pip3
DOCKER_COMPOSE := docker compose

# ── Colors ────────────────────────────────────────────────────
GREEN  := \033[0;32m
YELLOW := \033[1;33m
CYAN   := \033[0;36m
RESET  := \033[0m

help: ## Show this help message
	@echo ""
	@echo "$(CYAN)AI WhatsApp Automation Platform$(RESET)"
	@echo "────────────────────────────────────────────────"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-22s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ── Development ───────────────────────────────────────────────
install: ## Install all backend + frontend dependencies
	@echo "$(YELLOW)Installing backend dependencies...$(RESET)"
	cd backend && $(PIP) install -r requirements-dev.txt
	@echo "$(YELLOW)Installing frontend dependencies...$(RESET)"
	cd frontend && npm install

dev-backend: ## Start Flask dev server
	cd backend && flask run --debug --host=0.0.0.0 --port=5000

dev-frontend: ## Start React/Vite dev server
	cd frontend && npm run dev

dev-worker: ## Start Celery worker (dev)
	cd backend && celery -A app.tasks.celery_app:celery_app worker --loglevel=info -Q default,ai,workflows

dev-beat: ## Start Celery beat scheduler
	cd backend && celery -A app.tasks.celery_app:celery_app beat --loglevel=info

dev-all: ## Start all dev services via Docker Compose
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml up --build

# ── Database ──────────────────────────────────────────────────
migrate: ## Run Alembic migrations
	cd backend && alembic upgrade head

migrate-create: ## Create a new migration (MSG="description")
	cd backend && alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Rollback last migration
	cd backend && alembic downgrade -1

seed: ## Seed the database with initial data
	cd backend && $(PYTHON) scripts/seed_data.py

create-admin: ## Create a superadmin user
	cd backend && $(PYTHON) scripts/create_superadmin.py

generate-keys: ## Generate encryption & JWT keys
	cd backend && $(PYTHON) scripts/generate_keys.py

# ── Testing ───────────────────────────────────────────────────
test: ## Run all tests
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

test-unit: ## Run unit tests only
	cd backend && pytest tests/unit/ -v

test-integration: ## Run integration tests only
	cd backend && pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests
	cd backend && pytest tests/e2e/ -v

# ── Code Quality ──────────────────────────────────────────────
lint: ## Lint backend code (ruff + mypy)
	cd backend && ruff check app/ && mypy app/

lint-fix: ## Auto-fix lint issues
	cd backend && ruff check app/ --fix

format: ## Format code with black + isort
	cd backend && black app/ tests/ && isort app/ tests/

lint-frontend: ## Lint frontend code
	cd frontend && npm run lint

# ── Docker ────────────────────────────────────────────────────
docker-up: ## Start all services (production-like)
	$(DOCKER_COMPOSE) up --build -d

docker-up-dev: ## Start all services (dev)
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml up --build -d

docker-down: ## Stop all services
	$(DOCKER_COMPOSE) down

docker-logs: ## View all service logs
	$(DOCKER_COMPOSE) logs -f

docker-ps: ## List running containers
	$(DOCKER_COMPOSE) ps

docker-clean: ## Remove all containers, volumes, images
	$(DOCKER_COMPOSE) down -v --rmi all --remove-orphans

# ── Monitoring ────────────────────────────────────────────────
monitoring-up: ## Start monitoring stack (Prometheus + Grafana)
	$(DOCKER_COMPOSE) -f docker-compose.monitoring.yml up -d

monitoring-down: ## Stop monitoring stack
	$(DOCKER_COMPOSE) -f docker-compose.monitoring.yml down

# ── Security ──────────────────────────────────────────────────
security-scan: ## Run Bandit security scan on backend
	cd backend && bandit -r app/ -ll

secrets-check: ## Detect any committed secrets
	detect-secrets scan .

rotate-keys: ## Rotate encryption keys
	cd backend && $(PYTHON) scripts/generate_keys.py --rotate

# ── Build ─────────────────────────────────────────────────────
build-frontend: ## Build frontend for production
	cd frontend && npm run build

build-backend: ## Build backend Docker image
	docker build -t whatsapp-platform-backend ./backend

build-all: ## Build all Docker images
	$(DOCKER_COMPOSE) build

# ── Health ────────────────────────────────────────────────────
health: ## Run platform health check
	cd backend && $(PYTHON) scripts/health_check.py

# ── Clean ─────────────────────────────────────────────────────
clean: ## Clean build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf dist node_modules/.cache
	@echo "$(GREEN)Clean complete!$(RESET)"
