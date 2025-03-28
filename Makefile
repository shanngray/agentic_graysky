.PHONY: test test-unit test-integration test-health test-database run health-check clean

# Default target
all: test

# Run server
run:
	python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Testing
test:
	python tests/run_tests.py

test-unit:
	python tests/run_tests.py --types unit

test-integration:
	python tests/run_tests.py --types integration

test-health:
	python tests/run_tests.py --types health

test-database:
	python tests/run_tests.py --types database

# Health check
health-check:
	python scripts/health_check.py --url http://localhost:8080

health-check-prod:
	python scripts/health_check.py --url https://agentic-graysky.fly.dev

# Clean up
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -rf test_data/

# Create directory structure
setup-dirs:
	mkdir -p tests/unit tests/integration tests/health scripts test_data

# Help
help:
	@echo "Available targets:"
	@echo "  all            Run all tests (default)"
	@echo "  run            Run the development server"
	@echo "  test           Run all tests"
	@echo "  test-unit      Run unit tests"
	@echo "  test-integration Run integration tests"
	@echo "  test-health    Run health check tests"
	@echo "  test-database  Run database tests"
	@echo "  health-check   Run health check against local server"
	@echo "  health-check-prod Run health check against production"
	@echo "  clean          Clean up compiled files and caches"
	@echo "  setup-dirs     Create directory structure" 