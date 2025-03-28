#!/usr/bin/env python3
"""
Script to run all database tests.
"""

import unittest
import sys
import logging

def run_database_tests():
    """Run all tests for the database module."""
    # Suppress logging during tests
    logging.basicConfig(level=logging.CRITICAL)
    
    # Discover and run all tests in the tests directory
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('database/tests')
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return success or failure
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_database_tests()) 