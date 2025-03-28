import unittest
import os
import tempfile
import json
import requests
import shutil
import sqlite3
from database.connection import DatabaseConnection
from database.schema import create_tables

# Default test server URL
TEST_SERVER_URL = os.environ.get("TEST_SERVER_URL", "http://localhost:8080")

class TestDatabaseIntegration(unittest.TestCase):
    """Test database operations through the API."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary database file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_integration.db")
        
        # Set the database path in the environment for the API to use
        os.environ["DATABASE_PATH"] = self.db_path
        
        # Initialize the database
        self.db = DatabaseConnection(self.db_path)
        with self.db.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                INSERT INTO schema_version (version) VALUES (1);
            """)
        create_tables()
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory and database
        shutil.rmtree(self.temp_dir)
        # Reset environment variable
        if "DATABASE_PATH" in os.environ:
            del os.environ["DATABASE_PATH"]
    
    def test_visitor_persistence(self):
        """Test that visitors are persisted to the database."""
        # Create a test visitor via API
        test_visitor = {
            "name": "DB Integration Test",
            "agent_type": "Database Test",
            "purpose": "Testing database integration",
            "answers": {"test": "value"}
        }
        
        response = requests.post(f"{TEST_SERVER_URL}/welcome-book", json=test_visitor)
        self.assertEqual(response.status_code, 200)
        visitor_data = response.json()
        visitor_id = visitor_data["id"]
        
        # Verify entry was created in the database
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM visitors WHERE id = ?", (visitor_id,))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            
            # Verify the answers were stored as JSON
            cursor.execute("SELECT answers FROM visitors WHERE id = ?", (visitor_id,))
            answers_row = cursor.fetchone()
            if answers_row:
                answers = json.loads(answers_row[0])
                self.assertEqual(answers["test"], "value")
    
    def test_feedback_persistence(self):
        """Test that feedback is persisted to the database."""
        # Create test feedback via API
        test_feedback = {
            "agent_name": "DB Integration Test",
            "agent_type": "Database Test",
            "issues": "Testing issues",
            "feature_requests": "Test requests",
            "usability_rating": 8,
            "additional_comments": "Integration test comments"
        }
        
        response = requests.post(f"{TEST_SERVER_URL}/feedback", json=test_feedback)
        self.assertEqual(response.status_code, 200)
        feedback_data = response.json()
        
        # Verify entry was created in the database
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feedback WHERE agent_name = ?", (test_feedback["agent_name"],))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
    
    def test_transaction_integrity(self):
        """Test database transaction integrity."""
        # This test will verify that transactions are atomic
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Set up a trigger to enforce a constraint
            cursor.execute("""
                CREATE TRIGGER enforce_valid_rating
                BEFORE INSERT ON feedback
                BEGIN
                    SELECT CASE
                        WHEN NEW.usability_rating < 0 OR NEW.usability_rating > 10
                        THEN RAISE(ABORT, 'Rating must be between 0 and 10')
                    END;
                END;
            """)
        
        # Try to submit invalid feedback (rating out of range)
        test_feedback = {
            "agent_name": "DB Transaction Test",
            "agent_type": "Database Test",
            "issues": "Testing issues",
            "feature_requests": "Test requests",
            "usability_rating": 11,  # Invalid rating
            "additional_comments": "Transaction test comments"
        }
        
        response = requests.post(f"{TEST_SERVER_URL}/feedback", json=test_feedback)
        # Should get an error response
        self.assertNotEqual(response.status_code, 200)
        
        # Verify no entry was created
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM feedback WHERE agent_name = ?", 
                           (test_feedback["agent_name"],))
            count = cursor.fetchone()[0]
            self.assertEqual(count, 0)

if __name__ == "__main__":
    unittest.main() 