# ============================================================
# Makefile — Helper Commands
# Stock Prediction Portal
# ============================================================
# Usage: make <command>
# Example: make test, make build, make up

.PHONY: help up down build test logs clean lint format

# Default — help dikhao
help:
	@echo ""
	@echo "Stock Prediction Portal — Available Commands:"
	@echo "=============================================="
	@echo "  make up          -> Sab containers start karo"
	@echo "  make down        -> Sab containers band karo"
	@echo "  make build       -> Docker images rebuild karo"
	@echo "  make test        -> Saare tests run karo"
	@echo "  make logs        -> Backend logs dekho"
	@echo "  make lint        -> Code quality check karo"
	@echo "  make format      -> Code format karo"
	@echo "  make clean       -> Sab kuch clean karo"
	@echo "  make migrate     -> Database migrations run karo"
	@echo "  make shell       -> Django shell open karo"
	@echo "  make redis-flush -> Redis cache clear karo"
	@echo "  make push        -> GitHub pe push karo"
	@echo ""

# Containers start karo
up:
	docker compose up -d
	@echo "Sab containers start ho gaye!"
	@echo "   Frontend: http://localhost"
	@echo "   Backend:  http://localhost/api/v1/"

# Containers band karo
down:
	docker compose down
	@echo "Sab containers band ho gaye!"

# Rebuild + start
build:
	docker compose down
	docker compose up -d --build
	@echo "Naya build complete!"

# Saare tests run karo
test:
	@echo "Running backend tests..."
	docker compose exec backend pytest tests/ -v --tb=short
	@echo "Tests complete!"

# Tests with coverage
test-cov:
	docker compose exec backend pytest tests/ \
		--cov=api \
		--cov-report=term-missing \
		-v

# Backend logs
logs:
	docker compose logs backend -f --tail=50

# Frontend logs
logs-frontend:
	docker compose logs frontend -f --tail=50

# Saare logs
logs-all:
	docker compose logs -f --tail=30

# Code quality
lint:
	@echo "Running flake8..."
	docker compose exec backend flake8 api/ --max-line-length=120
	@echo "Lint complete!"

# Code format
format:
	@echo "Running black..."
	docker compose exec backend black api/ --line-length=120
	@echo "Format complete!"

# Database migration
migrate:
	docker compose exec backend python manage.py migrate
	@echo "Migrations complete!"

# Django shell
shell:
	docker compose exec backend python manage.py shell

# Redis cache flush
redis-flush:
	docker compose exec redis redis-cli -a redispass123 FLUSHALL
	@echo "Redis cache cleared!"

# Container status
status:
	docker compose ps

# Clean everything
clean:
	docker compose down -v
	docker system prune -f
	@echo "Sab clean!"

# GitHub push
push:
	git add .
	git status
	@read -p "Commit message: " msg; \
	git commit -m "$$msg"
	git push origin main
	@echo "GitHub pe push ho gaya!"
