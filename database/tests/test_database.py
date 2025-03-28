"""
Tests for database functionality.
"""

import os
import unittest
import tempfile
import sqlite3
from datetime import datetime

from database.connection import DatabaseConnection
from database.schema import create_tables
from database.visitor_db import add_visitor, get_visitor_by_id, get_visitors
from database.feedback_db import add_feedback, get_feedback

class TestDatabase(unittest.TestCase):
    """Test the database functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Configure database connection to use the temporary file
        self.db = DatabaseConnection(self.temp_db.name)
        
        # Create tables
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
        # Remove the temporary database file
        os.unlink(self.temp_db.name)
    
    def test_visitor_operations(self):
        """Test visitor CRUD operations."""
        # Add a visitor
        visitor_data = add_visitor(
            name="Test Visitor",
            agent_type="Test Agent",
            purpose="Testing",
            answers={"question1": "answer1", "question2": "answer2"}
        )
        
        # Check that the visitor was added
        self.assertIsNotNone(visitor_data)
        self.assertEqual(visitor_data["name"], "Test Visitor")
        self.assertEqual(visitor_data["agent_type"], "Test Agent")
        self.assertEqual(visitor_data["purpose"], "Testing")
        self.assertEqual(visitor_data["visit_count"], 1)
        
        # Get the visitor by ID
        visitor = get_visitor_by_id(visitor_data["id"])
        self.assertIsNotNone(visitor)
        self.assertEqual(visitor["name"], "Test Visitor")
        
        # Check answers
        self.assertEqual(visitor["answers"]["question1"], "answer1")
        self.assertEqual(visitor["answers"]["question2"], "answer2")
        
        # Get all visitors
        visitors = get_visitors()
        self.assertEqual(len(visitors), 1)
        
    def test_feedback_operations(self):
        """Test feedback CRUD operations."""
        # Add feedback
        feedback_data = add_feedback(
            agent_name="Test Agent",
            agent_type="Test Type",
            issues="Test issues",
            feature_requests="Test requests",
            usability_rating=8,
            additional_comments="Test comments"
        )
        
        # Check that the feedback was added
        self.assertIsNotNone(feedback_data)
        self.assertEqual(feedback_data["agent_name"], "Test Agent")
        self.assertEqual(feedback_data["agent_type"], "Test Type")
        self.assertEqual(feedback_data["issues"], "Test issues")
        self.assertEqual(feedback_data["usability_rating"], 8)
        
        # Get all feedback
        feedback_entries = get_feedback()
        self.assertEqual(len(feedback_entries), 1)
        
    def test_input_validation(self):
        """Test input validation."""
        # Test invalid name (too long)
        with self.assertRaises(ValueError):
            add_visitor(name="x" * 101)
            
        # Test invalid agent_type (too long)
        with self.assertRaises(ValueError):
            add_visitor(name="Test", agent_type="x" * 501)
            
        # Test invalid usability_rating
        with self.assertRaises(ValueError):
            add_feedback(agent_name="Test", usability_rating=11)
            
if __name__ == "__main__":
    unittest.main() 