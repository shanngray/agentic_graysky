import os
import pytest
from pathlib import Path

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
    
    # Make sure LITEFS_MOUNTED is not set in test environment
    if "LITEFS_MOUNTED" in os.environ:
        del os.environ["LITEFS_MOUNTED"]
    
    yield
    
    # Cleanup is optional here if you want tests to be inspectable afterwards 