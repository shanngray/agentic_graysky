import unittest
import os
import requests
import json
import socket
from datetime import datetime
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("deployment_tests")

# Get deployment URL from environment or default to production
DEPLOYMENT_URL = os.environ.get("DEPLOYMENT_URL", "https://agentic-graysky.fly.dev")

# Max retries for connection attempts
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

class TestDeployment(unittest.TestCase):
    """Post-deployment health checks for the API."""
    
    def setUp(self):
        """Set up test environment."""
        self.base_url = DEPLOYMENT_URL
        logger.info(f"Testing deployment at: {self.base_url}")
        
        # Get domain name for diagnostics
        self.domain = self.base_url.replace("https://", "").replace("http://", "").split("/")[0]
        try:
            logger.info(f"Resolving IP address for {self.domain}")
            ip_address = socket.gethostbyname(self.domain)
            logger.info(f"Domain {self.domain} resolves to {ip_address}")
        except socket.gaierror as e:
            logger.error(f"Failed to resolve domain {self.domain}: {e}")
    
    def make_request(self, url, method="get", json_data=None):
        """Make an HTTP request with retries."""
        for attempt in range(MAX_RETRIES):
            try:
                if method.lower() == "get":
                    response = requests.get(url, timeout=10)
                elif method.lower() == "post":
                    response = requests.post(url, json=json_data, timeout=10)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                return response
            except requests.exceptions.RequestException as e:
                logger.error(f"Request attempt {attempt+1}/{MAX_RETRIES} failed: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"All {MAX_RETRIES} attempts failed. Giving up.")
                    raise
    
    def test_health_endpoint(self):
        """Test the health endpoint of the deployed application."""
        try:
            response = self.make_request(f"{self.base_url}/health")
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
        except (requests.exceptions.RequestException, AssertionError) as e:
            logger.error(f"Health endpoint test failed: {str(e)}")
            raise
    
    def test_api_version_consistency(self):
        """Test that API version is consistent across endpoints."""
        try:
            # Get version from health endpoint
            health_response = self.make_request(f"{self.base_url}/health")
            health_data = health_response.json()
            
            # Get version from home endpoint
            home_response = self.make_request(f"{self.base_url}/")
            home_data = home_response.json()
            
            # Versions should match
            self.assertEqual(health_data["version"], home_data["info"]["version"])
        except (requests.exceptions.RequestException, AssertionError) as e:
            logger.error(f"API version consistency test failed: {str(e)}")
            raise
    
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
                try:
                    response = self.make_request(f"{self.base_url}{endpoint}")
                    self.assertEqual(response.status_code, 200)
                except (requests.exceptions.RequestException, AssertionError) as e:
                    logger.error(f"Endpoint {endpoint} test failed: {str(e)}")
                    raise
    
    def test_database_connection(self):
        """Test that the database is properly connected and functioning."""
        try:
            # Make a simple API request that requires database access
            response = self.make_request(f"{self.base_url}/welcome-book")
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
            
            response = self.make_request(f"{self.base_url}/welcome-book", method="post", json_data=test_visitor)
            self.assertEqual(response.status_code, 200)
            
            # Retrieve the record to verify database write/read
            response = self.make_request(f"{self.base_url}/welcome-book")
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
        except (requests.exceptions.RequestException, AssertionError) as e:
            logger.error(f"Database connection test failed: {str(e)}")
            raise
    
    def test_litefs_replication(self):
        """Test LiteFS replication if configured."""
        try:
            # This test is only relevant if LiteFS is enabled
            response = self.make_request(f"{self.base_url}/health")
            health_data = response.json()
            
            if health_data.get("litefs", {}).get("enabled", False):
                # If LiteFS is enabled, verify status
                self.assertIn("litefs", health_data)
                self.assertIn("status", health_data["litefs"])
                self.assertIn("role", health_data["litefs"])
                logger.info(f"LiteFS status: {health_data['litefs']['status']}, role: {health_data['litefs']['role']}")
                
                # Should be either "primary" or "replica"
                self.assertIn(health_data["litefs"]["role"], ["primary", "replica"])
        except (requests.exceptions.RequestException, AssertionError) as e:
            logger.error(f"LiteFS replication test failed: {str(e)}")
            raise

if __name__ == "__main__":
    unittest.main() 