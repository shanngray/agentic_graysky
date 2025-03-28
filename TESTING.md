# Agentic Graysky Testing Strategy

This document outlines the testing strategy for the Agentic Graysky API project.

## Test Categories

### Unit Tests
- Test individual components in isolation
- Verify API structure and endpoint responses
- Validate error handling and middleware functionality
- Mock external dependencies

### Integration Tests
- Test API endpoints against a running server
- Verify database operations through the API
- Test end-to-end workflows
- Validate data persistence

### Health Checks
- Verify deployment is healthy
- Check database connectivity
- Validate LiteFS replication (if enabled)
- Monitor system metrics

### Database Tests
- Test database schema and migrations
- Validate CRUD operations
- Test transaction integrity
- Verify error handling

## Test Environment

Tests can run in different environments:

1. **Local Development**: Run tests locally during development
2. **CI/CD Pipeline**: Run tests automatically on GitHub
3. **Post-Deployment**: Run health checks after deployment to Fly.io

## Running Tests

### Local Development

```bash
# Using the Makefile (recommended)
make test              # Run all tests
make test-unit         # Run unit tests
make test-integration  # Run integration tests
make test-health       # Run health checks
make test-database     # Run database tests

# Or using the test runner directly
python tests/run_tests.py
python tests/run_tests.py --types unit integration
```

### CI/CD Pipeline

The GitHub workflow runs tests automatically:
1. Unit tests run before deployment
2. If unit tests pass, the application is deployed to Fly.io
3. Health checks run after deployment

## Test Configuration

The project uses a global `conftest.py` file in the project root to configure pytest and provide common fixtures:

```python
# Key fixtures provided:
setup_test_environment  # Sets up environment variables for testing
test_db_path            # Provides path to test database
```

Tests can be configured using environment variables:

- `TEST_SERVER_URL`: URL of the test server (default: http://localhost:8080)
- `LITEFS_DB_PATH`: Path to the test database file
- `DATABASE_PATH`: Alias for the database path
- `TESTING`: Flag to indicate test environment

## Health Checks

You can run health checks manually against any deployment:

```bash
# Check local development server
make health-check

# Check production deployment
make health-check-prod

# Using the script directly with custom URL
python scripts/health_check.py --url https://your-deployment-url
```

## Troubleshooting Common Issues

### Database Connection Issues

If tests fail with database connection errors:

1. Check if the database file exists
2. Verify permissions on the database directory
3. Check if SQLite is installed

### Integration Test Failures

If integration tests fail:

1. Ensure the test server is running
2. Check if the API endpoint exists
3. Verify database connection is working

### Health Check Failures

If health checks fail after deployment:

1. Check if the application is running
2. Verify the health endpoint is accessible
3. Check if the database is connected
4. Look for error logs in Fly.io dashboard

## Maintenance

Regular test maintenance tasks:

1. Run `make clean` to remove cached files and test artifacts
2. Update test fixtures when database schema changes
3. Review and update test environment variables as needed

## Continuous Improvement

This testing strategy should evolve over time:

1. Add more test coverage as new features are added
2. Improve test automation in the CI/CD pipeline
3. Add performance testing for critical operations
4. Monitor test results and address failures promptly 