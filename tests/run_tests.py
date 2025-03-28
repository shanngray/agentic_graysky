#!/usr/bin/env python3
"""
Main test runner script for the Agentic Graysky API.
Discovers and runs tests from all test directories.
"""

import unittest
import sys
import os
import argparse
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_runner")

def run_tests(test_types: Optional[List[str]] = None) -> int:
    """
    Run all tests for the API.
    
    Args:
        test_types: Optional list of test types to run. Options: "unit", "integration", "health", "database".
                   If None, all tests are run.
    
    Returns:
        int: 0 if all tests passed, 1 otherwise
    """
    if test_types is None:
        test_types = ["unit", "integration", "health", "database"]
    
    logger.info(f"Running test types: {', '.join(test_types)}")
    
    # Set up the test loader
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add unit tests
    if "unit" in test_types:
        logger.info("Loading unit tests...")
        unit_tests = test_loader.discover('tests/unit', pattern='test_*.py')
        test_suite.addTests(unit_tests)
    
    # Add integration tests
    if "integration" in test_types:
        logger.info("Loading integration tests...")
        integration_tests = test_loader.discover('tests/integration', pattern='test_*.py')
        test_suite.addTests(integration_tests)
    
    # Add health check tests
    if "health" in test_types:
        logger.info("Loading health check tests...")
        health_tests = test_loader.discover('tests/health', pattern='test_*.py')
        test_suite.addTests(health_tests)
    
    # Add database tests
    if "database" in test_types:
        logger.info("Loading database tests...")
        database_tests = test_loader.discover('database/tests', pattern='test_*.py')
        test_suite.addTests(database_tests)
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return success or failure
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tests for the Agentic Graysky API")
    parser.add_argument(
        '--types', 
        type=str, 
        nargs='*',
        choices=['unit', 'integration', 'health', 'database', 'all'],
        default=['all'],
        help="Types of tests to run"
    )
    
    args = parser.parse_args()
    
    # If 'all' is selected, run all test types
    test_types = None if 'all' in args.types else args.types
    
    # Run the tests
    exit_code = run_tests(test_types)
    sys.exit(exit_code) 