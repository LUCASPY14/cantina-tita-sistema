# Makefile para Sistema de Gestión de Cantina
# Automatiza comandos comunes de desarrollo y despliegue

.PHONY: help setup dev test migrate deploy clean docker-build docker-up docker-down docker-logs lint format coverage

# Variables
PYTHON := python
PIP := pip
MANAGE := cd backend && $(PYTHON) manage.py
NPM := cd frontend && npm
DOCKER_COMPOSE := docker-compose
VENV := .venv

# Colores para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

##@ Ayuda

help: ## Mostrar esta ayuda
	@echo "$(BLUE)Sistema de Gestión de Cantina - Comandos Make$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\nUso:\n  make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup

setup: ## Configuración inicial completa del proyecto
	@echo "$(GREEN)🚀 Configurando proyecto...$(NC)"
	@echo "$(YELLOW)📦 Creando entorno virtual Python...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(YELLOW)📥 Instalando dependencias Python...$(NC)"
	$(VENV)/Scripts/pip install --upgrade pip
	$(VENV)/Scripts/pip install -r backend/requirements.txt
	@echo "$(YELLOW)📥 Instalando dependencias Node.js...$(NC)"
	$(NPM) install
	@echo "$(YELLOW)📝 Copiando .env.example a .env...$(NC)"
	@if not exist .env copy .env.example .env
	@echo "$(GREEN)✅ Setup completado!$(NC)"
	@echo "$(BLUE)💡 Edita .env con tus configuraciones antes de continuar$(NC)"

setup-env: ## Crear archivo .env desde .env.example
	@if not exist .env (copy .env.example .env && echo "$(GREEN)✅ .env creado desde .env.example$(NC)") else (echo "$(YELLOW)⚠️  .env ya existe$(NC)")

##@ Desarrollo

dev: ## Iniciar servidor de desarrollo (Django + Vite)
	@echo "$(GREEN)🚀 Iniciando servidores de desarrollo...$(NC)"
	$(PYTHON) dev_server.py

dev-backend: ## Iniciar solo Django backend
	@echo "$(GREEN)🐍 Iniciando Django en http://localhost:8000$(NC)"
	$(MANAGE) runserver

dev-frontend: ## Iniciar solo Vite frontend
	@echo "$(GREEN)⚡ Iniciando Vite en http://localhost:5173$(NC)"
	$(NPM) run dev

shell: ## Abrir Django shell
	$(MANAGE) shell

dbshell: ## Abrir MySQL shell
	$(MANAGE) dbshell

##@ Base de Datos

migrate: ## Ejecutar migraciones de Django
	@echo "$(YELLOW)🔄 Ejecutando migraciones...$(NC)"
	$(MANAGE) migrate

makemigrations: ## Crear nuevas migraciones
	@echo "$(YELLOW)📝 Creando migraciones...$(NC)"
	$(MANAGE) makemigrations

showmigrations: ## Mostrar estado de migraciones
	$(MANAGE) showmigrations

flush-db: ## Limpiar base de datos (CUIDADO!)
	@echo "$(RED)⚠️  ADVERTENCIA: Esto borrará todos los datos!$(NC)"
	$(MANAGE) flush --noinput

##@ Testing

test: ## Ejecutar tests backend con pytest
	@echo "$(YELLOW)🧪 Ejecutando tests backend...$(NC)"
	pytest -v

test-unit: ## Ejecutar solo tests unitarios
	@echo "$(YELLOW)🧪 Ejecutando tests unitarios...$(NC)"
	pytest -m unit -v

test-integration: ## Ejecutar tests de integración
	@echo "$(YELLOW)🧪 Ejecutando tests de integración...$(NC)"
	pytest -m integration -v

test-coverage: ## Ejecutar tests con reporte de coverage
	@echo "$(YELLOW)📊 Ejecutando tests con coverage...$(NC)"
	pytest --cov --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✅ Reporte generado en htmlcov/index.html$(NC)"

test-watch: ## Ejecutar tests en modo watch
	@echo "$(YELLOW)👀 Tests en modo watch...$(NC)"
	pytest -f

test-frontend: ## Ejecutar tests frontend con Vitest
	@echo "$(YELLOW)🧪 Ejecutando tests frontend...$(NC)"
	cd frontend && $(NPM) run test:coverage

test-e2e: ## Ejecutar tests E2E con Playwright
	@echo "$(YELLOW)🎭 Ejecutando tests E2E...$(NC)"
	npx playwright test

test-all: ## Ejecutar todos los tests (backend, frontend, E2E)
	@echo "$(YELLOW)🧪 Ejecutando TODOS los tests...$(NC)"
	@$(MAKE) test-coverage
	@$(MAKE) test-frontend
	@$(MAKE) test-e2e
	@echo "$(GREEN)✅ Todos los tests completados$(NC)"

lint: ## Ejecutar linters (flake8, eslint)
	@echo "$(YELLOW)🔍 Ejecutando linters...$(NC)"
	@echo "$(BLUE)Python (flake8)...$(NC)"
	-$(VENV)/Scripts/flake8 backend/gestion backend/pos
	@echo "$(BLUE)JavaScript/TypeScript (eslint)...$(NC)"
	-$(NPM) run lint

format: ## Formatear código (black, prettier)
	@echo "$(YELLOW)✨ Formateando código...$(NC)"
	@echo "$(BLUE)Python (black)...$(NC)"
	-$(VENV)/Scripts/black backend/gestion backend/pos
	@echo "$(BLUE)JavaScript/TypeScript (prettier)...$(NC)"
	-$(NPM) run format

##@ Build

build: ## Compilar frontend para producción
	@echo "$(YELLOW)📦 Compilando frontend...$(NC)"
	$(NPM) run build

collectstatic: ## Recolectar archivos estáticos de Django
	@echo "$(YELLOW)📦 Recolectando archivos estáticos...$(NC)"
	$(MANAGE) collectstatic --noinput

build-all: build collectstatic ## Build completo (frontend + static)
	@echo "$(GREEN)✅ Build completo finalizado$(NC)"

##@ Docker

docker-build: ## Construir imágenes Docker
	@echo "$(YELLOW)🐳 Construyendo imágenes Docker...$(NC)"
	$(DOCKER_COMPOSE) build

docker-up: ## Iniciar contenedores Docker
	@echo "$(GREEN)🐳 Iniciando contenedores...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Contenedores iniciados$(NC)"
	@echo "$(BLUE)💡 Django: http://localhost:8000$(NC)"
	@echo "$(BLUE)💡 Nginx: http://localhost$(NC)"

docker-down: ## Detener contenedores Docker
	@echo "$(YELLOW)🐳 Deteniendo contenedores...$(NC)"
	$(DOCKER_COMPOSE) down

docker-restart: docker-down docker-up ## Reiniciar contenedores Docker

docker-logs: ## Ver logs de contenedores
	$(DOCKER_COMPOSE) logs -f

docker-logs-django: ## Ver logs solo de Django
	$(DOCKER_COMPOSE) logs -f django

docker-ps: ## Listar contenedores en ejecución
	$(DOCKER_COMPOSE) ps

docker-clean: ## Limpiar contenedores, volúmenes e imágenes
	@echo "$(RED)⚠️  Limpiando Docker...$(NC)"
	$(DOCKER_COMPOSE) down -v --rmi local

docker-shell: ## Abrir shell en contenedor Django
	$(DOCKER_COMPOSE) exec django /bin/bash

docker-migrate: ## Ejecutar migraciones en Docker
	$(DOCKER_COMPOSE) exec django python manage.py migrate

##@ Utilidades

clean: ## Limpiar archivos temporales y cache
	@echo "$(YELLOW)🧹 Limpiando archivos temporales...$(NC)"
	@if exist __pycache__ rd /s /q __pycache__
	@if exist .pytest_cache rd /s /q .pytest_cache
	@if exist htmlcov rd /s /q htmlcov
	@if exist .coverage del .coverage
	@for /r %%i in (*.pyc) do @del "%%i"
	@for /r %%i in (*.pyo) do @del "%%i"
	@echo "$(BLUE)Frontend cleanup...$(NC)"
	@if exist frontend\dist rd /s /q frontend\dist
	@if exist frontend\.vite rd /s /q frontend\.vite
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

clean-migrations: ## Eliminar archivos de migraciones (CUIDADO!)
	@echo "$(RED)⚠️  Eliminando archivos de migraciones...$(NC)"
	@for /r backend\gestion\migrations %%i in (*.py) do @if not "%%~nxi"=="__init__.py" del "%%i"
	@for /r backend\pos\migrations %%i in (*.py) do @if not "%%~nxi"=="__init__.py" del "%%i"

install-pre-commit: ## Instalar pre-commit hooks
	@echo "$(YELLOW)🪝 Instalando pre-commit hooks...$(NC)"
	$(VENV)/Scripts/pip install pre-commit
	$(VENV)/Scripts/pre-commit install
	@echo "$(GREEN)✅ Pre-commit hooks instalados$(NC)"

update-deps: ## Actualizar dependencias
	@echo "$(YELLOW)📦 Actualizando dependencias...$(NC)"
	$(VENV)/Scripts/pip install --upgrade -r backend/requirements.txt
	$(NPM) update
	@echo "$(GREEN)✅ Dependencias actualizadas$(NC)"

check: ## Ejecutar Django system check
	$(MANAGE) check

backup-db: ## Crear backup de la base de datos
	@echo "$(YELLOW)💾 Creando backup...$(NC)"
	$(MANAGE) dumpdata --natural-foreign --natural-primary > backup_$$(date +%Y%m%d_%H%M%S).json
	@echo "$(GREEN)✅ Backup creado$(NC)"

##@ Producción

deploy: build-all docker-build docker-up ## Deploy completo (build + docker)
	@echo "$(GREEN)🚀 Deploy completado!$(NC)"

deploy-check: ## Verificar configuración de producción
	@echo "$(YELLOW)🔍 Verificando configuración...$(NC)"
	$(MANAGE) check --deploy
	@echo "$(GREEN)✅ Verificación completada$(NC)"

##@ Información

version: ## Mostrar versiones de dependencias
	@echo "$(BLUE)📦 Versiones de dependencias:$(NC)"
	@echo "$(YELLOW)Python:$(NC)"
	@$(PYTHON) --version
	@echo "$(YELLOW)Django:$(NC)"
	@$(VENV)/Scripts/python -c "import django; print(django.get_version())"
	@echo "$(YELLOW)Node.js:$(NC)"
	@node --version
	@echo "$(YELLOW)npm:$(NC)"
	@npm --version

status: ## Mostrar estado del proyecto
	@echo "$(BLUE)📊 Estado del Proyecto$(NC)"
	@echo "$(YELLOW)Entorno virtual:$(NC) $$(if exist $(VENV) (echo ✅ Existe) else (echo ❌ No existe))"
	@echo "$(YELLOW)Archivo .env:$(NC) $$(if exist .env (echo ✅ Existe) else (echo ❌ No existe))"
	@echo "$(YELLOW)Docker:$(NC)"
	@$(DOCKER_COMPOSE) ps

##@ Default

.DEFAULT_GOAL := help
