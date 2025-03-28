# Agentic Graysky API Tests

This directory contains the testing suite for the Agentic Graysky API.

## Test Structure

The tests are organized into several categories:

- **Unit Tests** (`tests/unit/`): Basic tests for API structure and functionality
- **Integration Tests** (`tests/integration/`): Tests that verify API functionality against a running server
- **Health Checks** (`tests/health/`): Tests for post-deployment health verification
- **Database Tests** (`database/tests/`): Tests for database functionality

## Running Tests

You can run all tests using the main test runner:

```bash
python tests/run_tests.py
```

To run specific test categories:

```bash
python tests/run_tests.py --types unit integration
```

Available test types:
- `unit`: Unit tests
- `integration`: Integration tests
- `health`: Health check tests
- `database`: Database tests
- `all`: All test types (default)

## Environment Variables

Tests can be configured with these environment variables:

- `TEST_SERVER_URL`: URL of the test server (default: http://localhost:8080)
- `START_TEST_SERVER`: Whether to start a test server (default: True)
- `DEPLOYMENT_URL`: URL of the deployed application for health checks
- `DATABASE_PATH`: Path to the database file for testing

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