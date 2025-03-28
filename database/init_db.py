"""
Script to initialize the database and run migrations.
Can be run directly to set up the database.
"""

import argparse
import logging
import sys
import os
import sqlite3
from pathlib import Path

from database.schema import initialize_database
from database.migration import migrate_all_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def create_sqlite_schema():
    """Initialize the SQLite database with the required schema."""
    db_path = os.environ.get('LITEFS_DB_PATH', '/var/lib/litefs/data/graysky.db')
    
    logger.info(f"Initializing database at {db_path}")
    
    # Check if database directory exists
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        logger.info(f"Creating database directory: {db_dir}")
        os.makedirs(db_dir, exist_ok=True)
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create welcome_book table
        logger.info("Creating welcome_book table")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS welcome_book (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create feedback table
        logger.info("Creating feedback table")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            message TEXT NOT NULL,
            rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Add any other tables needed for your application
        
        conn.commit()
        logger.info("Database initialization completed successfully")
        
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def setup_database(with_migration: bool = False) -> None:
    """
    Set up the database with tables and optionally migrate data.
    
    Args:
        with_migration: Whether to migrate data from JSON files
    """
    try:
        logger.info("Initializing database...")
        initialize_database()
        logger.info("Database initialized successfully")
        
        if with_migration:
            logger.info("Migrating data from JSON files...")
            results = migrate_all_data()
            logger.info(f"Migration completed: {results}")
            
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Initialize Agentic Graysky database")
    parser.add_argument(
        "--migrate", 
        action="store_true", 
        help="Migrate data from JSON files"
    )
    args = parser.parse_args()
    
    # Run database setup
    create_sqlite_schema()
    setup_database(with_migration=args.migrate) 