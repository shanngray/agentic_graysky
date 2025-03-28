import os
import sys
import pytest
from pathlib import Path

# Add the project root to the Python path to make imports work
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Test database file for SQLite
TEST_DB_PATH = Path("./test_data/test_graysky.db")

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Setup test environment with a local database path instead of /var/lib/litefs
    """
    # Create a temporary test directory
    test_dir = Path("./test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Set environment variables for testing
    os.environ["LITEFS_DB_PATH"] = str(test_dir / "test_graysky.db")
    os.environ["DATABASE_PATH"] = str(test_dir / "test_graysky.db")
    os.environ["TESTING"] = "True"
    os.environ["TEST_SERVER_URL"] = "http://localhost:8080"
    
    # Make sure LITEFS_MOUNTED is not set in test environment
    if "LITEFS_MOUNTED" in os.environ:
        del os.environ["LITEFS_MOUNTED"]
    
    yield
    
    # Cleanup is optional here if you want tests to be inspectable afterwards

@pytest.fixture(scope="session")
def test_db_path():
    """Provide a test database path for testing."""
    return str(TEST_DB_PATH) 