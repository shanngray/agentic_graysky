import unittest
import os
import requests
import time
import subprocess
import signal
import sys
from multiprocessing import Process

# Default test server URL
TEST_SERVER_URL = os.environ.get("TEST_SERVER_URL", "http://localhost:8080")
# Whether to start a test server or use an existing one
START_TEST_SERVER = os.environ.get("START_TEST_SERVER", "True").lower() == "true"

def start_server():
    """Start a test server instance."""
    # Run uvicorn with the main app
    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"],
        env=dict(os.environ, **{"TESTING": "True"})
    )
    # Give the server time to start
    time.sleep(3)

class TestLiveApi(unittest.TestCase):
    """Test the API against a live server."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        if START_TEST_SERVER:
            cls.server_process = Process(target=start_server)
            cls.server_process.start()
            # Give time for server to start
            time.sleep(3)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        if START_TEST_SERVER and hasattr(cls, 'server_process'):
            cls.server_process.terminate()
            cls.server_process.join(timeout=2)
    
    def test_health_endpoint(self):
        """Test the health endpoint."""
        response = requests.get(f"{TEST_SERVER_URL}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("database", data)
        self.assertIn("version", data)
    
    def test_welcome_book_workflow(self):
        """Test creating and retrieving welcome book entries."""
        # Test visitor data
        test_visitor = {
            "name": "Test Integration Agent",
            "agent_type": "Integration Test",
            "purpose": "Testing API endpoints",
            "answers": {
                "model": "Test Framework",
                "purpose": "API Integration",
                "preference": "JSON"
            }
        }
        
        # Post to welcome book
        response = requests.post(f"{TEST_SERVER_URL}/welcome-book", json=test_visitor)
        self.assertEqual(response.status_code, 200)
        post_data = response.json()
        
        # Verify response fields
        self.assertEqual(post_data["name"], test_visitor["name"])
        self.assertEqual(post_data["agent_type"], test_visitor["agent_type"])
        self.assertIn("id", post_data)
        
        # Get the welcome book entries
        response = requests.get(f"{TEST_SERVER_URL}/welcome-book")
        self.assertEqual(response.status_code, 200)
        get_data = response.json()
        
        # Verify our entry exists
        self.assertIsInstance(get_data, list)
        # Find our entry
        matching_entries = [entry for entry in get_data if entry.get("id") == post_data["id"]]
        self.assertEqual(len(matching_entries), 1)

if __name__ == "__main__":
    unittest.main() 