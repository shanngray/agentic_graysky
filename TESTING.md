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
# Run all tests
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py --types unit integration
```

### CI/CD Pipeline

The GitHub workflow runs tests automatically:
1. Unit tests run before deployment
2. If unit tests pass, the application is deployed to Fly.io
3. Health checks run after deployment

## Test Configuration

Tests can be configured using environment variables:

- `TEST_SERVER_URL`: URL of the test server
- `START_TEST_SERVER`: Whether to start a test server
- `DEPLOYMENT_URL`: URL of the deployed application
- `DATABASE_PATH`: Path to the test database

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

## Continuous Improvement

This testing strategy should evolve over time:

1. Add more test coverage as new features are added
2. Improve test automation in the CI/CD pipeline
3. Add performance testing for critical operations
4. Monitor test results and address failures promptly 