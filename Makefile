# Huginn Data Insights - Makefile
.PHONY: help install test lint format build run clean docker-up docker-down logs

help:
	@echo "Huginn Data Insights - Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"
	@echo "  make build      - Build Docker image"
	@echo "  make run        - Run application locally"
	@echo "  make docker-up  - Start services with Docker Compose"
	@echo "  make docker-down- Stop Docker Compose services"
	@echo "  make logs       - View Docker Compose logs"
	@echo "  make clean      - Clean temporary files"

install:
	pip install -r requirements-dev.txt

test:
	python -m pytest tests/ -v --cov=src --cov-report=html

lint:
	flake8 src/ tests/
	isort --check-only src/ tests/
	black --check src/ tests/

format:
	isort src/ tests/
	black src/ tests/

build:
	docker build -t huginn-data-insights .

run:
	streamlit run app.py

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov
	rm -rf build/ dist/ *.egg-info