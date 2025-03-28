"""
Database schema definitions and migrations for the Agentic Graysky application.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Optional

from database.connection import db

# Configure logger
logger = logging.getLogger("graysky_api.database.schema")

# Schema version
SCHEMA_VERSION = 1

# SQL to create the visitors table
CREATE_VISITORS_TABLE = """
CREATE TABLE IF NOT EXISTS visitors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    agent_type TEXT,
    purpose TEXT,
    visit_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    visit_count INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT name_length CHECK(length(name) <= 100),
    CONSTRAINT agent_type_length CHECK(length(agent_type) <= 500),
    CONSTRAINT purpose_length CHECK(length(purpose) <= 500)
);
"""

# SQL to create the answers table
CREATE_ANSWERS_TABLE = """
CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visitor_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    FOREIGN KEY (visitor_id) REFERENCES visitors(id) ON DELETE CASCADE,
    CONSTRAINT key_length CHECK(length(key) <= 50),
    CONSTRAINT value_length CHECK(length(value) <= 500)
);
"""

# SQL to create the feedback table
CREATE_FEEDBACK_TABLE = """
CREATE TABLE IF NOT EXISTS feedback (
    id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    agent_type TEXT,
    submission_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    issues TEXT,
    feature_requests TEXT,
    usability_rating INTEGER,
    additional_comments TEXT,
    CONSTRAINT agent_name_length CHECK(length(agent_name) <= 100),
    CONSTRAINT agent_type_length CHECK(length(agent_type) <= 500),
    CONSTRAINT issues_length CHECK(length(issues) <= 2000),
    CONSTRAINT feature_requests_length CHECK(length(feature_requests) <= 2000),
    CONSTRAINT additional_comments_length CHECK(length(additional_comments) <= 2000),
    CONSTRAINT usability_rating_range CHECK(usability_rating BETWEEN 1 AND 10)
);
"""

# SQL to create the schema_version table
CREATE_SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def create_tables() -> None:
    """Create all database tables if they don't exist."""
    try:
        logger.info("Creating database tables if they don't exist")
        with db.get_connection() as conn:
            # Execute table creation scripts
            conn.executescript(CREATE_VISITORS_TABLE)
            conn.executescript(CREATE_ANSWERS_TABLE)
            conn.executescript(CREATE_FEEDBACK_TABLE)
            conn.executescript(CREATE_SCHEMA_VERSION_TABLE)
            
            # Set initial schema version if not exists
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
            result = cursor.fetchone()
            
            if not result:
                cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
                logger.info(f"Initialized schema to version {SCHEMA_VERSION}")
            else:
                current_version = result["version"]
                logger.info(f"Current schema version: {current_version}")
                
                # Apply any necessary migrations
                if current_version < SCHEMA_VERSION:
                    apply_migrations(conn, current_version, SCHEMA_VERSION)
            
            conn.commit()
        logger.info("Database tables created successfully")
    except sqlite3.Error as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def apply_migrations(conn: sqlite3.Connection, from_version: int, to_version: int) -> None:
    """
    Apply database migrations from current version to target version.
    
    Args:
        conn: SQLite connection
        from_version: Current schema version
        to_version: Target schema version
    """
    logger.info(f"Applying migrations from version {from_version} to {to_version}")
    
    # Define migrations here when needed
    # Example:
    # if from_version < 2 and to_version >= 2:
    #     conn.executescript("ALTER TABLE visitors ADD COLUMN new_field TEXT;")
    
    # Update schema version
    conn.execute("INSERT INTO schema_version (version) VALUES (?)", (to_version,))
    logger.info(f"Schema updated to version {to_version}")

def import_json_data() -> None:
    """Import data from JSON files into the database (for initial migration)."""
    # This will be implemented later when needed for data migration
    pass

def initialize_database() -> None:
    """Initialize the database with tables and initial data."""
    create_tables()
    # Import JSON data if needed later
    # import_json_data() 