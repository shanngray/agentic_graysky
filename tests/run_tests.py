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
from pathlib import Path
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_runner")

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Add project root to Python path
sys.path.insert(0, str(PROJECT_ROOT))

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
        unit_tests_dir = os.path.join(PROJECT_ROOT, 'tests', 'unit')
        if os.path.exists(unit_tests_dir):
            unit_tests = test_loader.discover(unit_tests_dir, pattern='test_*.py')
            test_suite.addTests(unit_tests)
        else:
            logger.warning(f"Unit tests directory not found: {unit_tests_dir}")
    
    # Add integration tests
    if "integration" in test_types:
        logger.info("Loading integration tests...")
        integration_tests_dir = os.path.join(PROJECT_ROOT, 'tests', 'integration')
        if os.path.exists(integration_tests_dir):
            integration_tests = test_loader.discover(integration_tests_dir, pattern='test_*.py')
            test_suite.addTests(integration_tests)
        else:
            logger.warning(f"Integration tests directory not found: {integration_tests_dir}")
    
    # Add health check tests
    if "health" in test_types:
        logger.info("Loading health check tests...")
        health_tests_dir = os.path.join(PROJECT_ROOT, 'tests', 'health')
        if os.path.exists(health_tests_dir):
            health_tests = test_loader.discover(health_tests_dir, pattern='test_*.py')
            test_suite.addTests(health_tests)
        else:
            logger.warning(f"Health tests directory not found: {health_tests_dir}")
    
    # Add database tests
    if "database" in test_types:
        logger.info("Loading database tests...")
        database_tests_dir = os.path.join(PROJECT_ROOT, 'database', 'tests')
        if os.path.exists(database_tests_dir):
            try:
                # Load database tests individually
                for file in Path(database_tests_dir).glob('test_*.py'):
                    module_name = f"database.tests.{file.stem}"
                    try:
                        # Import the test module
                        __import__(module_name)
                        module = sys.modules[module_name]
                        
                        # Add all test cases from this module
                        for name in dir(module):
                            obj = getattr(module, name)
                            if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and obj != unittest.TestCase:
                                test_suite.addTest(test_loader.loadTestsFromTestCase(obj))
                                
                    except (ImportError, AttributeError) as e:
                        logger.error(f"Error loading test module {module_name}: {e}")
            except Exception as e:
                logger.error(f"Error discovering database tests: {e}")
        else:
            logger.warning(f"Database tests directory not found: {database_tests_dir}")
    
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