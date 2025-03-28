"""
Database package for the Agentic Graysky application.
Contains SQLite connection utilities, schema definitions, and data access layers.
"""

# Connection utilities
from database.connection import db, DatabaseConnection

# Database schema
from database.schema import initialize_database, create_tables

# Data models
from database.model import Visitor, VisitorCreate, Feedback, FeedbackCreate

# Data access layers
from database.visitor_db import (
    add_visitor, 
    get_visitors, 
    get_visitor_by_id, 
    get_visitor_by_name_and_agent_type
)
from database.feedback_db import (
    add_feedback, 
    get_feedback, 
    get_feedback_by_id, 
    get_feedback_by_agent_name
)

# Migration utilities
from database.migration import migrate_all_data, import_welcome_book_data, import_feedback_data

# Initialization
from database.init_db import setup_database

__all__ = [
    # Connection
    'db', 'DatabaseConnection',
    
    # Schema
    'initialize_database', 'create_tables',
    
    # Models
    'Visitor', 'VisitorCreate', 'Feedback', 'FeedbackCreate',
    
    # Visitor operations
    'add_visitor', 'get_visitors', 'get_visitor_by_id', 'get_visitor_by_name_and_agent_type',
    
    # Feedback operations
    'add_feedback', 'get_feedback', 'get_feedback_by_id', 'get_feedback_by_agent_name',
    
    # Migration
    'migrate_all_data', 'import_welcome_book_data', 'import_feedback_data',
    
    # Initialization
    'setup_database',
] 