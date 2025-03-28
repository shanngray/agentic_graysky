"""
Migration utilities for importing data from JSON files into SQLite database.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from database.connection import db
from database.visitor_db import add_visitor
from database.feedback_db import add_feedback
from database.schema import create_tables

# Configure logger
logger = logging.getLogger("graysky_api.database.migration")

def import_welcome_book_data(json_file: str = "data/welcome_book.json") -> int:
    """
    Import visitor data from JSON file into the database.
    
    Args:
        json_file: Path to the JSON file
        
    Returns:
        Number of imported visitors
    """
    try:
        path = Path(json_file)
        if not path.exists():
            logger.warning(f"JSON file not found: {json_file}")
            return 0
            
        with open(path, 'r', encoding='utf-8') as f:
            visitors_data = json.load(f)
            
        if not visitors_data:
            logger.info(f"No visitors found in {json_file}")
            return 0
            
        count = 0
        for visitor in visitors_data:
            try:
                # Extract data
                name = visitor.get("name")
                agent_type = visitor.get("agent_type")
                purpose = visitor.get("purpose")
                answers = visitor.get("answers", {})
                
                # Add to database
                add_visitor(
                    name=name,
                    agent_type=agent_type,
                    purpose=purpose,
                    answers=answers
                )
                count += 1
                
            except Exception as e:
                logger.error(f"Error importing visitor: {e}")
                logger.error(f"Visitor data: {visitor}")
                continue
                
        logger.info(f"Imported {count} visitors from {json_file}")
        return count
        
    except Exception as e:
        logger.error(f"Error importing visitors from {json_file}: {e}")
        return 0

def import_feedback_data(json_file: str = "data/feedback.json") -> int:
    """
    Import feedback data from JSON file into the database.
    
    Args:
        json_file: Path to the JSON file
        
    Returns:
        Number of imported feedback entries
    """
    try:
        path = Path(json_file)
        if not path.exists():
            logger.warning(f"JSON file not found: {json_file}")
            return 0
            
        with open(path, 'r', encoding='utf-8') as f:
            feedback_data = json.load(f)
            
        if not feedback_data:
            logger.info(f"No feedback found in {json_file}")
            return 0
            
        count = 0
        for feedback in feedback_data:
            try:
                # Extract data
                agent_name = feedback.get("agent_name")
                agent_type = feedback.get("agent_type")
                issues = feedback.get("issues")
                feature_requests = feedback.get("feature_requests")
                usability_rating = feedback.get("usability_rating")
                additional_comments = feedback.get("additional_comments")
                
                # Add to database
                add_feedback(
                    agent_name=agent_name,
                    agent_type=agent_type,
                    issues=issues,
                    feature_requests=feature_requests,
                    usability_rating=usability_rating,
                    additional_comments=additional_comments
                )
                count += 1
                
            except Exception as e:
                logger.error(f"Error importing feedback: {e}")
                logger.error(f"Feedback data: {feedback}")
                continue
                
        logger.info(f"Imported {count} feedback entries from {json_file}")
        return count
        
    except Exception as e:
        logger.error(f"Error importing feedback from {json_file}: {e}")
        return 0

def migrate_all_data() -> Dict[str, int]:
    """
    Migrate all data from JSON files to the database.
    
    Returns:
        Dictionary with counts of migrated data
    """
    # Ensure tables exist
    create_tables()
    
    # Import data
    visitor_count = import_welcome_book_data()
    feedback_count = import_feedback_data()
    
    return {
        "visitors": visitor_count,
        "feedback": feedback_count
    } 