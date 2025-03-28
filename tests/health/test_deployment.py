import unittest
import os
import requests
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("deployment_tests")

# Get deployment URL from environment or default to production
DEPLOYMENT_URL = os.environ.get("DEPLOYMENT_URL", "https://agentic-graysky.fly.dev")

class TestDeployment(unittest.TestCase):
    """Post-deployment health checks for the API."""
    
    def setUp(self):
        """Set up test environment."""
        self.base_url = DEPLOYMENT_URL
        logger.info(f"Testing deployment at: {self.base_url}")
    
    def test_health_endpoint(self):
        """Test the health endpoint of the deployed application."""
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify health data
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("database", data)
        self.assertEqual(data["database"]["status"], "connected")
        self.assertIn("version", data)
        
        # Log deployment info
        logger.info(f"Deployment version: {data['version']}")
        logger.info(f"Uptime: {data.get('uptime', 'unknown')}")
        
        # Check if server timestamp is within reasonable range
        if "timestamp" in data:
            server_time = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
            local_time = datetime.utcnow()
            time_diff = abs((local_time - server_time).total_seconds())
            # Server time should be within 30 seconds of local time
            self.assertLess(time_diff, 30)
    
    def test_api_version_consistency(self):
        """Test that API version is consistent across endpoints."""
        # Get version from health endpoint
        health_response = requests.get(f"{self.base_url}/health")
        health_data = health_response.json()
        
        # Get version from home endpoint
        home_response = requests.get(f"{self.base_url}/")
        home_data = home_response.json()
        
        # Versions should match
        self.assertEqual(health_data["version"], home_data["info"]["version"])
    
    def test_basic_endpoints(self):
        """Test that basic API endpoints are accessible."""
        endpoints = [
            "/",
            "/about",
            "/welcome-book",
            "/articles",
            "/projects"
        ]
        
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = requests.get(f"{self.base_url}{endpoint}")
                self.assertEqual(response.status_code, 200)
    
    def test_database_connection(self):
        """Test that the database is properly connected and functioning."""
        # Make a simple API request that requires database access
        response = requests.get(f"{self.base_url}/welcome-book")
        self.assertEqual(response.status_code, 200)
        
        # Add a test visitor
        test_visitor = {
            "name": "Deployment Test",
            "agent_type": "Health Check",
            "purpose": "Verifying deployment health",
            "answers": {
                "deployment_time": datetime.utcnow().isoformat()
            }
        }
        
        response = requests.post(f"{self.base_url}/welcome-book", json=test_visitor)
        self.assertEqual(response.status_code, 200)
        
        # Retrieve the record to verify database write/read
        response = requests.get(f"{self.base_url}/welcome-book")
        self.assertEqual(response.status_code, 200)
        entries = response.json()
        
        # Find our test entry
        found = False
        for entry in entries:
            if (entry.get("name") == test_visitor["name"] and 
                entry.get("agent_type") == test_visitor["agent_type"]):
                found = True
                break
        
        self.assertTrue(found, "Failed to retrieve test entry from database")
    
    def test_litefs_replication(self):
        """Test LiteFS replication if configured."""
        # This test is only relevant if LiteFS is enabled
        response = requests.get(f"{self.base_url}/health")
        health_data = response.json()
        
        if health_data.get("litefs", {}).get("enabled", False):
            # If LiteFS is enabled, verify status
            self.assertIn("litefs", health_data)
            self.assertIn("status", health_data["litefs"])
            self.assertIn("role", health_data["litefs"])
            logger.info(f"LiteFS status: {health_data['litefs']['status']}, role: {health_data['litefs']['role']}")
            
            # Should be either "primary" or "replica"
            self.assertIn(health_data["litefs"]["role"], ["primary", "replica"])

if __name__ == "__main__":
    unittest.main() 