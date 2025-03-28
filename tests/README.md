# Agentic Graysky API Tests

This directory contains the testing suite for the Agentic Graysky API.

## Test Structure

The tests are organized into several categories:

- **Unit Tests** (`tests/unit/`): Basic tests for API structure and functionality
- **Integration Tests** (`tests/integration/`): Tests that verify API functionality against a running server
- **Health Checks** (`tests/health/`): Tests for post-deployment health verification
- **Database Tests** (`database/tests/`): Tests for database functionality

## Running Tests

You can run all tests using the main test runner or the Makefile:

```bash
# Using the test runner directly
python tests/run_tests.py

# Using Make
make test

# Run specific test categories using Make
make test-unit
make test-integration
make test-health
make test-database
```

Available test types:
- `unit`: Unit tests
- `integration`: Integration tests
- `health`: Health check tests
- `database`: Database tests
- `all`: All test types (default)

## Test Configuration

The project uses two configuration files for tests:

1. `conftest.py` in the project root: Sets up the test environment with:
   - Local database path configuration
   - Environment variables for testing
   - Various test fixtures

2. `tests/run_tests.py`: Custom test runner that:
   - Discovers and runs tests from different directories
   - Allows running specific test categories
   - Integrates with the CI/CD pipeline

## Health Checks

The project includes two health check components:

1. `health_check.py`: API endpoint module that:
   - Provides the `/health` endpoint for the API
   - Checks database connectivity
   - Reports system metrics and LiteFS status

2. `scripts/health_check.py`: Standalone client script that:
   - Can be run against any deployment
   - Reports health status in text or JSON format
   - Run using `make health-check` or `make health-check-prod`

## CI/CD Pipeline

The tests are integrated into the CI/CD pipeline:

1. GitHub workflow runs unit and database tests
2. If tests pass, deploys to Fly.io
3. After deployment, runs health checks against the deployed instance

## Adding New Tests

1. Create test files in the appropriate directory
2. Follow the naming convention `test_*.py`
3. Implement tests using the `unittest` framework
4. Run the tests to verify they work as expected

## Troubleshooting

If tests fail with import errors:
- Ensure `PYTHONPATH` includes the project root
- Verify that `conftest.py` is correctly setting up the environment
- Check if the test runner is finding the correct test files 