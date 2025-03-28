"""
Data access layer for feedback table.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

import sqlite3
from database.connection import db

# Configure logger
logger = logging.getLogger("graysky_api.database.feedback_db")

def get_feedback(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent feedback entries from the database.
    
    Args:
        limit: Maximum number of feedback entries to return
    
    Returns:
        List of feedback dictionaries
    """
    query = """
    SELECT id, agent_name, agent_type, submission_time, issues, 
           feature_requests, usability_rating, additional_comments
    FROM feedback 
    ORDER BY submission_time DESC 
    LIMIT ?
    """
    
    try:
        return db.execute_query(query, (limit,))
    except sqlite3.Error as e:
        logger.error(f"Error retrieving feedback: {e}")
        raise

def get_feedback_by_id(feedback_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a feedback entry by ID.
    
    Args:
        feedback_id: The feedback ID
        
    Returns:
        Feedback dictionary or None if not found
    """
    query = """
    SELECT id, agent_name, agent_type, submission_time, issues, 
           feature_requests, usability_rating, additional_comments
    FROM feedback 
    WHERE id = ?
    """
    
    try:
        results = db.execute_query(query, (feedback_id,))
        return results[0] if results else None
    except sqlite3.Error as e:
        logger.error(f"Error retrieving feedback {feedback_id}: {e}")
        raise

def get_feedback_by_agent_name(agent_name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get feedback entries by agent name.
    
    Args:
        agent_name: The agent name
        limit: Maximum number of feedback entries to return
        
    Returns:
        List of feedback dictionaries
    """
    query = """
    SELECT id, agent_name, agent_type, submission_time, issues, 
           feature_requests, usability_rating, additional_comments
    FROM feedback 
    WHERE agent_name = ?
    ORDER BY submission_time DESC 
    LIMIT ?
    """
    
    try:
        return db.execute_query(query, (agent_name, limit))
    except sqlite3.Error as e:
        logger.error(f"Error retrieving feedback for agent {agent_name}: {e}")
        raise

def add_feedback(agent_name: str, agent_type: Optional[str] = None, 
                issues: Optional[str] = None, feature_requests: Optional[str] = None,
                usability_rating: Optional[int] = None, 
                additional_comments: Optional[str] = None) -> Dict[str, Any]:
    """
    Add a new feedback entry to the database.
    
    Args:
        agent_name: Agent's name
        agent_type: Agent's type
        issues: Reported issues
        feature_requests: Requested features
        usability_rating: Rating from 1-10
        additional_comments: Additional comments
        
    Returns:
        The created feedback dictionary
    """
    # Validate input
    if not agent_name or len(agent_name) > 100:
        raise ValueError("Agent name is required and must be 100 characters or less")
    
    if agent_type and len(agent_type) > 500:
        raise ValueError("Agent type must be 500 characters or less")
        
    if issues and len(issues) > 2000:
        raise ValueError("Issues text must be 2000 characters or less")
        
    if feature_requests and len(feature_requests) > 2000:
        raise ValueError("Feature requests must be 2000 characters or less")
        
    if additional_comments and len(additional_comments) > 2000:
        raise ValueError("Additional comments must be 2000 characters or less")
        
    if usability_rating is not None and not (1 <= usability_rating <= 10):
        raise ValueError("Usability rating must be between 1 and 10")
    
    feedback_id = str(uuid.uuid4())
    submission_time = datetime.now()
    
    # Insert new feedback
    insert_query = """
    INSERT INTO feedback (
        id, agent_name, agent_type, submission_time, issues, 
        feature_requests, usability_rating, additional_comments
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    try:
        db.execute_update(
            insert_query, 
            (feedback_id, agent_name, agent_type, submission_time, 
            issues, feature_requests, usability_rating, additional_comments)
        )
        
        # Return the complete feedback record
        return {
            "id": feedback_id,
            "agent_name": agent_name,
            "agent_type": agent_type,
            "submission_time": submission_time,
            "issues": issues,
            "feature_requests": feature_requests,
            "usability_rating": usability_rating,
            "additional_comments": additional_comments
        }
    except sqlite3.Error as e:
        logger.error(f"Error adding feedback: {e}")
        raise 