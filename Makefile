.PHONY: help bootstrap lint format test testreport migrate serve outdated clean
DEFAULT: help

VENV = .venv
PYTHON = $(VENV)/bin/python

ADMIN_POSTGRES_USER ?= postgis
ADMIN_POSTGRES_PASSWORD ?= postgis
ADMIN_POSTGRES_DATABASE ?= postgis

APPLICATION_POSTGRES_HOST ?= 127.0.0.1
APPLICATION_POSTGRES_PORT ?= 5432
APPLICATION_POSTGRES_USER ?= application
APPLICATION_POSTGRES_PASSWORD ?= application
APPLICATION_POSTGRES_DATABASE ?= application

PG_ADMIN_URL ?= postgresql://$(ADMIN_POSTGRES_USER):$(ADMIN_POSTGRES_PASSWORD)@$(APPLICATION_POSTGRES_HOST):$(APPLICATION_POSTGRES_PORT)/$(ADMIN_POSTGRES_DATABASE)
PG_APPLICATION_URL ?= postgresql://$(APPLICATION_POSTGRES_USER):$(APPLICATION_POSTGRES_PASSWORD)@$(APPLICATION_POSTGRES_HOST):$(APPLICATION_POSTGRES_PORT)/$(APPLICATION_POSTGRES_DATABASE)

help:
	@echo "Available targets:"
	@echo "  help       - show this text"
	@echo "  bootstrap  - setup development environment"
	@echo "  lint       - run static analysis"
	@echo "  format     - format code style"
	@echo "  test       - run project tests"
	@echo "  testreport - report test coverage"
	@echo "  migrate    - create database and run migrations"
	@echo "  serve      - run project in debug mode"
	@echo "  outdated   - show outdated pip packages"
	@echo "  clean      - clean up development artifacts"

bootstrap:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip wheel setuptools
	$(PYTHON) -m pip install -e .[dev]

lint: $(VENV)
	$(PYTHON) -m ruff check application tests

format: $(VENV)
	$(PYTHON) -m ruff format application tests
	$(PYTHON) -m ruff check --fix application tests

test: $(VENV)
	$(PYTHON) -m pytest

testreport: $(VENV)
	$(PYTHON) -m pytest --cov=application --cov-report=term-missing --cov-report=xml --cov-report=html

migrate: $(VENV)
	psql $(PG_ADMIN_URL) -c "CREATE ROLE application WITH ENCRYPTED PASSWORD 'application' CREATEDB LOGIN;" || true
	psql $(PG_ADMIN_URL) -c "CREATE DATABASE application WITH OWNER application;" || true
	psql $(PG_APPLICATION_URL) -c "CREATE EXTENSION pg_trgm;" || true
	$(PYTHON) -m alembic upgrade head

serve: $(VENV)
	APPLICATION_WEB_DEBUG=1 $(PYTHON) -m uvicorn application.web:app --reload

outdated: $(VENV)
	$(PYTHON) -m pip list --outdated

clean:
	rm -rf $(VENV) .coverage .pytest_cache .ruff_cache coverage.xml htmlcov application.egg-info
	find -type d -name __pycache__ | xargs rm -rf
