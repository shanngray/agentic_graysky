#!/usr/bin/env python3
"""
Demonstration of database functionality.
This script initializes the database, performs various operations,
and displays the results.
"""

import logging
import sys
from datetime import datetime

from database.init_db import setup_database
from database.visitor_db import add_visitor, get_visitors, get_visitor_by_id
from database.feedback_db import add_feedback, get_feedback
from database.migration import migrate_all_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("graysky_api.database.demo")

def run_demo():
    """Run a demonstration of database functionality."""
    try:
        # Initialize the database with migrations
        logger.info("Initializing database...")
        setup_database(with_migration=True)
        
        # Add a new visitor
        logger.info("Adding a new visitor...")
        visitor = add_visitor(
            name="Demo Visitor",
            agent_type="Demo Agent",
            purpose="Demonstration",
            answers={
                "favorite_feature": "SQLite integration",
                "feedback_rating": 9,
                "suggestions": "Add more database features"
            }
        )
        logger.info(f"Added visitor: {visitor}")
        
        # Add feedback
        logger.info("Adding feedback...")
        feedback = add_feedback(
            agent_name="Demo Visitor",
            agent_type="Demo Agent",
            issues="No issues found",
            feature_requests="More database features",
            usability_rating=9,
            additional_comments="The database integration is working well!"
        )
        logger.info(f"Added feedback: {feedback}")
        
        # Get all visitors
        logger.info("Getting visitors...")
        visitors = get_visitors(limit=10)
        logger.info(f"Found {len(visitors)} visitors")
        for i, v in enumerate(visitors):
            logger.info(f"Visitor {i+1}: {v['name']} ({v['agent_type']})")
            logger.info(f"  Answers: {v['answers']}")
        
        # Get all feedback
        logger.info("Getting feedback...")
        feedback_entries = get_feedback(limit=10)
        logger.info(f"Found {len(feedback_entries)} feedback entries")
        for i, f in enumerate(feedback_entries):
            logger.info(f"Feedback {i+1}: {f['agent_name']} - Rating: {f['usability_rating']}")
            if f['issues']:
                logger.info(f"  Issues: {f['issues']}")
            if f['feature_requests']:
                logger.info(f"  Feature requests: {f['feature_requests']}")
        
        logger.info("Demo completed successfully")
        return 0
    
    except Exception as e:
        logger.error(f"Error in demo: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_demo()) 