.PHONY: help clean lint format test test-thread test-coverage run install docker-build docker-run all-checks

# Variables
PYTHON = python
PIP = pip
APP_MODULE = app.main:app
PORT = 8000
APP_DIR = app
TEST_DIR = tests
THREAD_COUNT ?= 2
DOCKER_TAG = latest
DOCKER_IMAGE = ai-based-toc-builder

help:
	@echo "Available commands:"
	@echo "  make help                - Show this help message"
	@echo "  make install             - Install dependencies"
	@echo "  make lint                - Run linters (flake8, mypy)"
	@echo "  make format              - Format code with black"
	@echo "  make format-check        - Check if code needs formatting"
	@echo "  make test                - Run all tests"
	@echo "  make test-thread         - Run thread optimization tests"
	@echo "  make test-coverage       - Run tests with coverage report"
	@echo "  make clean               - Remove build artifacts"
	@echo "  make run                 - Run the application locally"
	@echo "  make docker-build        - Build the Docker image"
	@echo "  make docker-run          - Run the application in Docker"
	@echo "  make all-checks          - Run all linting and tests"

install:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

lint:
	@echo "Running flake8..."
	$(PYTHON) -m flake8 $(APP_DIR) $(TEST_DIR) --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "Running mypy..."
	$(PYTHON) -m mypy $(APP_DIR)

format:
	$(PYTHON) -m black $(APP_DIR) $(TEST_DIR)

format-check:
	$(PYTHON) -m black --check $(APP_DIR) $(TEST_DIR)

test:
	$(PYTHON) -m pytest $(TEST_DIR) -v

test-thread:
	THREAD_COUNT=$(THREAD_COUNT) $(PYTHON) -m pytest $(TEST_DIR)/utils/test_process_image_thread.py -v

test-benchmark:
	$(PYTHON) -m pytest $(TEST_DIR)/utils/test_process_image_thread.py::test_benchmark_pdf_conversion -v

test-coverage:
	$(PYTHON) -m pytest --cov=$(APP_DIR) $(TEST_DIR) --cov-report=term --cov-report=html
	@echo "HTML coverage report generated in htmlcov/"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

run:
	uvicorn $(APP_MODULE) --host 0.0.0.0 --port $(PORT) --reload

docker-build:
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run:
	docker run -p $(PORT):$(PORT) $(DOCKER_IMAGE):$(DOCKER_TAG)

all-checks: format-check lint test

# Default target
.DEFAULT_GOAL := help
