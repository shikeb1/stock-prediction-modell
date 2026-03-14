.PHONY: help build up down logs test migrations shell format lint

# ========================================================================
# MAKEFILE - DEVELOPMENT COMMANDS
# ========================================================================
#
# Usage: make <command>
# Example: make up
#
# Ye file development shortcuts provide karta hai
#
# ========================================================================

help:
	@echo "=========================================="
	@echo "Stock Prediction Portal - Development"
	@echo "=========================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make build              - Build Docker images"
	@echo "  make setup              - First-time setup (.env + resources)"
	@echo ""
	@echo "Container Commands:"
	@echo "  make up                 - Start all services"
	@echo "  make down               - Stop all services"
	@echo "  make restart            - Restart all services"
	@echo "  make logs               - View container logs"
	@echo ""
	@echo "Backend Commands:"
	@echo "  make migrations         - Create Django migrations"
	@echo "  make migrate            - Apply migrations"
	@echo "  make test               - Run all tests"
	@echo "  make test-backend       - Run backend tests only"
	@echo "  make test-ml            - Run ML tests only"
	@echo "  make test-coverage      - Run tests with coverage"
	@echo "  make shell              - Django shell"
	@echo "  make createsuperuser    - Create admin user"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint               - Run flake8 linter"
	@echo "  make format             - Format code with black"
	@echo "  make format-check       - Check code format"
	@echo ""
	@echo "Database:"
	@echo "  make db-clean           - Delete database (warning!)"
	@echo "  make db-seed            - Seed sample data"
	@echo ""
	@echo "Other:"
	@echo "  make clean              - Clean build files"
	@echo ""

# ========================================================================
# SETUP COMMANDS
# ========================================================================

setup:
	@echo "🔧 Setting up Stock Prediction Portal..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file (please update with your values)"; \
	fi
	@if [ ! -d resources ]; then \
		mkdir -p resources; \
		echo "✅ Created resources/ folder"; \
	fi
	@echo "⚠️  Next steps:"
	@echo "   1. Edit .env with your settings"
	@echo "   2. Place stock_prediction_model.keras in resources/"
	@echo "   3. Run: make build && make up"

build:
	@echo "🏗️  Building Docker images..."
	docker-compose build --no-cache
	@echo "✅ Build complete!"

# ========================================================================
# CONTAINER COMMANDS
# ========================================================================

up:
	@echo "🚀 Starting all services..."
	docker-compose up -d
	@sleep 5
	@echo "✅ Services started!"
	@echo ""
	@echo "📍 Access points:"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/api/schema/swagger/"
	@echo ""
	@echo "View logs: make logs"

down:
	@echo "🛑 Stopping all services..."
	docker-compose down
	@echo "✅ Services stopped!"

restart:
	@echo "🔄 Restarting services..."
	docker-compose restart
	@echo "✅ Services restarted!"

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

# ========================================================================
# BACKEND COMMANDS
# ========================================================================

migrations:
	@echo "📝 Creating Django migrations..."
	docker-compose exec backend python manage.py makemigrations
	@echo "✅ Migrations created!"

migrate:
	@echo "🗄️  Applying migrations..."
	docker-compose exec backend python manage.py migrate
	@echo "✅ Migrations applied!"

test:
	@echo "✅ Running all tests..."
	docker-compose exec backend pytest tests/ -v --cov=api --cov=accounts --cov-report=term-missing
	@echo ""
	@echo "✅ Tests complete!"

test-backend:
	@echo "✅ Running backend integration tests..."
	docker-compose exec backend pytest tests/test_api.py -v
	@echo "✅ Tests complete!"

test-ml:
	@echo "✅ Running ML model tests..."
	docker-compose exec backend pytest tests/test_ml.py -v
	@echo "✅ Tests complete!"

test-coverage:
	@echo "📊 Running tests with coverage..."
	docker-compose exec backend pytest tests/ \
		--cov=api \
		--cov=accounts \
		--cov-report=html \
		--cov-report=term-missing
	@echo "✅ Coverage report: htmlcov/index.html"

shell:
	@echo "🐍 Opening Django shell..."
	docker-compose exec backend python manage.py shell

createsuperuser:
	@echo "👑 Creating superuser..."
	docker-compose exec backend python manage.py createsuperuser

manage:
	docker-compose exec backend python manage.py $(cmd)

# ========================================================================
# CODE QUALITY
# ========================================================================

lint:
	@echo "🔍 Running Flake8 linter..."
	@pip install flake8 >/dev/null 2>&1 || true
	flake8 backend-drf/api backend-drf/accounts --max-line-length=100 || true
	@echo "✅ Linting complete!"

format:
	@echo "🎨 Formatting code with black..."
	@pip install black >/dev/null 2>&1 || true
	black backend-drf/ --line-length=100
	@echo "✅ Formatting complete!"

format-check:
	@echo "🔍 Checking code format..."
	@pip install black >/dev/null 2>&1 || true
	black backend-drf/ --check || true
	@echo "✅ Format check complete!"

# ========================================================================
# DATABASE
# ========================================================================

db-clean:
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose down -v; \
		docker-compose up -d; \
		make migrate; \
		echo "✅ Database cleaned and reset!"; \
	else \
		echo "❌ Cancelled"; \
	fi

db-seed:
	@echo "🌱 Seeding sample data..."
	docker-compose exec backend python manage.py shell < backend-drf/seed_data.py
	@echo "✅ Data seeded!"

# ========================================================================
# UTILITIES
# ========================================================================

clean:
	@echo "🧹 Cleaning build files..."
	find . -type d -name __pycache__ -exec rm -r {} + >/dev/null 2>&1 || true
	find . -type d -name .pytest_cache -exec rm -r {} + >/dev/null 2>&1 || true
	find . -type d -name htmlcov -exec rm -r {} + >/dev/null 2>&1 || true
	find . -type d -name .eggs -exec rm -r {} + >/dev/null 2>&1 || true
	find . -type d -name *.egg-info -exec rm -r {} + >/dev/null 2>&1 || true
	@echo "✅ Cleanup complete!"

# ========================================================================
# QUICK COMMANDS
# ========================================================================

runserver:
	@echo "🚀 Running development server..."
	docker-compose exec backend python manage.py runserver 0.0.0.0:8000

npm-install:
	@echo "📦 Installing npm packages..."
	docker-compose exec frontend npm install

npm-update:
	@echo "📦 Updating npm packages..."
	docker-compose exec frontend npm update

# ========================================================================
# DEFAULT COMMAND
# ========================================================================

.DEFAULT_GOAL := help

# ========================================================================
# END OF MAKEFILE
# ========================================================================
#
# Notes:
# - Make sure Docker is running
# - docker-compose must be installed
# - Run 'make setup' first time
# - Run 'make help' to see all commands
#
# Common workflow:
#   1. make setup       (first time only)
#   2. make build       (build images)
#   3. make up          (start services)
#   4. make test        (run tests)
#   5. make down        (stop when done)
#
