"""
Data access layer for visitors and answers tables.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union

import sqlite3
from database.connection import db
from database.schema import create_tables

# Configure logger
logger = logging.getLogger("graysky_api.database.visitor_db")

def initialize() -> None:
    """Initialize the visitor database tables."""
    create_tables()

def get_visitors(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent visitors from the database.
    
    Args:
        limit: Maximum number of visitors to return
    
    Returns:
        List of visitor dictionaries
    """
    query = """
    SELECT id, name, agent_type, purpose, visit_time, visit_count 
    FROM visitors 
    ORDER BY visit_time DESC 
    LIMIT ?
    """
    
    try:
        visitors = db.execute_query(query, (limit,))
        
        # Get answers for each visitor
        for visitor in visitors:
            visitor_id = visitor["id"]
            visitor["answers"] = get_visitor_answers(visitor_id)
            
        return visitors
    except sqlite3.Error as e:
        logger.error(f"Error retrieving visitors: {e}")
        raise

def get_visitor_by_id(visitor_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a visitor by ID.
    
    Args:
        visitor_id: The visitor's ID
        
    Returns:
        Visitor dictionary or None if not found
    """
    query = """
    SELECT id, name, agent_type, purpose, visit_time, visit_count 
    FROM visitors 
    WHERE id = ?
    """
    
    try:
        results = db.execute_query(query, (visitor_id,))
        if not results:
            return None
            
        visitor = results[0]
        visitor["answers"] = get_visitor_answers(visitor_id)
        return visitor
    except sqlite3.Error as e:
        logger.error(f"Error retrieving visitor {visitor_id}: {e}")
        raise

def get_visitor_by_name_and_agent_type(name: str, agent_type: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Get a visitor by name and agent type.
    
    Args:
        name: The visitor's name
        agent_type: The visitor's agent type
        
    Returns:
        Visitor dictionary or None if not found
    """
    # Define parameters with appropriate type hint
    params: Union[Tuple[str, str], Tuple[str]]
    
    if agent_type:
        query = """
        SELECT id, name, agent_type, purpose, visit_time, visit_count 
        FROM visitors 
        WHERE name = ? AND agent_type = ?
        """
        params = (name, agent_type)
    else:
        query = """
        SELECT id, name, agent_type, purpose, visit_time, visit_count 
        FROM visitors 
        WHERE name = ? AND agent_type IS NULL
        """
        params = (name,)
    
    try:
        results = db.execute_query(query, params)
        if not results:
            return None
            
        visitor = results[0]
        visitor["answers"] = get_visitor_answers(visitor["id"])
        return visitor
    except sqlite3.Error as e:
        logger.error(f"Error retrieving visitor by name {name} and agent type {agent_type}: {e}")
        raise

def get_visitor_answers(visitor_id: str) -> Dict[str, Any]:
    """
    Get answers for a visitor.
    
    Args:
        visitor_id: The visitor's ID
        
    Returns:
        Dictionary of answers (key-value pairs)
    """
    query = """
    SELECT key, value 
    FROM answers 
    WHERE visitor_id = ?
    """
    
    try:
        results = db.execute_query(query, (visitor_id,))
        
        # Convert list of key-value rows to a dictionary
        answers = {}
        for row in results:
            answers[row["key"]] = row["value"]
            
        return answers
    except sqlite3.Error as e:
        logger.error(f"Error retrieving answers for visitor {visitor_id}: {e}")
        raise

def add_visitor(name: str, agent_type: Optional[str] = None, purpose: Optional[str] = None, 
                answers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Add a new visitor to the database.
    
    Args:
        name: Visitor's name
        agent_type: Visitor's agent type
        purpose: Visitor's purpose
        answers: Visitor's answers as key-value pairs
        
    Returns:
        The created visitor dictionary
    """
    # Validate name length
    if not name or len(name) > 100:
        raise ValueError("Name is required and must be 100 characters or less")
    
    # Validate agent_type and purpose length
    if agent_type and len(agent_type) > 500:
        raise ValueError("Agent type must be 500 characters or less")
        
    if purpose and len(purpose) > 500:
        raise ValueError("Purpose must be 500 characters or less")
        
    # Check for existing visitor with same name and agent_type
    existing_visitor = get_visitor_by_name_and_agent_type(name, agent_type)
    visit_count = 1
    
    visitor_id = str(uuid.uuid4())
    visit_time = datetime.now()
    
    if existing_visitor:
        visitor_id = existing_visitor["id"]
        visit_count = existing_visitor["visit_count"] + 1
        
        # Update existing visitor
        update_query = """
        UPDATE visitors 
        SET visit_time = ?, visit_count = ? 
        WHERE id = ?
        """
        db.execute_update(update_query, (visit_time, visit_count, visitor_id))
    else:
        # Insert new visitor
        insert_query = """
        INSERT INTO visitors (id, name, agent_type, purpose, visit_time, visit_count) 
        VALUES (?, ?, ?, ?, ?, ?)
        """
        db.execute_update(insert_query, (visitor_id, name, agent_type, purpose, visit_time, visit_count))
    
    # Add answers if provided
    if answers:
        add_visitor_answers(visitor_id, answers)
    
    # Return the complete visitor record
    return {
        "id": visitor_id,
        "name": name,
        "agent_type": agent_type,
        "purpose": purpose,
        "visit_time": visit_time,
        "visit_count": visit_count,
        "answers": answers or {}
    }

def add_visitor_answers(visitor_id: str, answers: Dict[str, Any]) -> None:
    """
    Add answers for a visitor.
    
    Args:
        visitor_id: The visitor's ID
        answers: Dictionary of answers (key-value pairs)
    """
    if not answers:
        return
        
    # Delete existing answers for this visitor
    delete_query = "DELETE FROM answers WHERE visitor_id = ?"
    db.execute_update(delete_query, (visitor_id,))
    
    # Insert new answers
    insert_query = "INSERT INTO answers (visitor_id, key, value) VALUES (?, ?, ?)"
    
    try:
        with db.get_connection() as conn:
            for key, value in answers.items():
                # Validate key and value
                if not key or len(key) > 50:
                    logger.warning(f"Skipping answer with invalid key: {key[:50]}...")
                    continue
                    
                # Convert value to string if it's not already
                str_value = str(value)
                if len(str_value) > 500:
                    logger.warning(f"Truncating answer value for key {key}")
                    str_value = str_value[:500]
                
                conn.execute(insert_query, (visitor_id, key, str_value))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error adding answers for visitor {visitor_id}: {e}")
        raise 