#!/usr/bin/env python
"""
Test runner script for the Graysky Agent API.
This script runs the test suite with detailed output and generates a report.
"""

import subprocess
import sys
import datetime
import os

def main():
    """Run the test suite and output results."""
    print("=" * 80)
    print(f"Running Graysky Agent API tests - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Create data directory for tests if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Check if pytest is installed, if not install via uv
    try:
        import pytest
    except ImportError:
        print("Installing pytest via uv...")
        try:
            subprocess.run(["uv", "pip", "install", "pytest", "httpx"], check=True)
        except subprocess.CalledProcessError:
            print("Failed to install pytest via uv. Please install it manually with:")
            print("  uv pip install pytest httpx")
            return 1
        except FileNotFoundError:
            print("uv command not found. Please install it or make sure it's in your PATH.")
            print("To install pytest manually: uv pip install pytest httpx")
            return 1
    
    # Run the tests with detailed output
    result = subprocess.run(
        [
            sys.executable, 
            "-m", 
            "pytest", 
            "tests.py", 
            "-v",  # Verbose output
            "--no-header",  # Skip pytest header
            "--color=yes",  # Colorized output
        ],
        capture_output=True,
        text=True,
    )
    
    # Print test output
    print(result.stdout)
    
    if result.stderr:
        print("\nErrors encountered:")
        print(result.stderr)
    
    # Exit with the same code as pytest
    return result.returncode

if __name__ == "__main__":
    sys.exit(main()) 