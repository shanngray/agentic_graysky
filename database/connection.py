"""
SQLite connection utilities for the Agentic Graysky application.
Provides connection management, pooling, and error handling.
"""

import sqlite3
import os
import logging
import threading
from contextlib import contextmanager
from typing import Dict, Generator, Any, Union, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Thread-local storage for database connections
_local = threading.local()

# Get the database path from environment variables
def get_db_path() -> str:
    """Get the SQLite database path from environment variables."""
    return os.environ.get('LITEFS_DB_PATH', '/var/lib/litefs/data/graysky.db')

def get_connection() -> sqlite3.Connection:
    """Get a SQLite connection from the thread-local pool."""
    if not hasattr(_local, 'connection'):
        db_path = get_db_path()
        logger.debug(f"Creating new database connection to {db_path}")
        
        # Create connection with row factory for dictionary-like access
        _local.connection = sqlite3.connect(db_path)
        _local.connection.row_factory = sqlite3.Row
        
        # Enable foreign keys and other pragma settings
        _local.connection.execute("PRAGMA foreign_keys = ON")
    
    return _local.connection

@contextmanager
def get_db_cursor() -> Generator[sqlite3.Cursor, None, None]:
    """Get a database cursor as a context manager."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()

@contextmanager
def transaction() -> Generator[sqlite3.Connection, None, None]:
    """Execute operations within a transaction."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def close_connection() -> None:
    """Close the database connection for the current thread."""
    if hasattr(_local, 'connection'):
        _local.connection.close()
        del _local.connection
        logger.debug("Database connection closed")

def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> Dict[str, Any]:
    """Convert SQLite row objects to dictionaries."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def execute_query(query: str, params: tuple = ()) -> list:
    """Execute a query and return all results."""
    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

def execute_update(query: str, params: tuple = ()) -> int:
    """Execute an update query and return the number of affected rows."""
    with transaction() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.rowcount

class DatabaseConnection:
    """Database connection manager for SQLite with LiteFS support."""
    
    def __init__(self, db_path: str = get_db_path()):
        """
        Initialize database connection manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_directory()
        
    def _ensure_db_directory(self) -> None:
        """Ensure the database directory exists."""
        # Skip directory creation for LiteFS mounts
        if os.environ.get('LITEFS_MOUNTED'):
            return
            
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Created database directory: {db_dir}")
    
    def get_connection(self, for_write: bool = False) -> sqlite3.Connection:
        """
        Get a SQLite connection with proper configuration.
        
        Args:
            for_write: If True, ensures connection can write (only on primary node)
            
        Returns:
            sqlite3.Connection: Configured SQLite connection
        """
        try:
            # Check if we're trying to write on a replica
            is_primary = os.environ.get('LITEFS_PRIMARY', 'true').lower() == 'true'
            if for_write and not is_primary:
                logger.error("Attempted write operation on replica node")
                raise sqlite3.Error("Write operations not allowed on replica nodes")
            
            # Enable foreign keys and configure for proper timestamp handling
            conn = sqlite3.connect(
                self.db_path, 
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Configure connection to return rows as dictionaries
            conn.row_factory = sqlite3.Row
            
            return conn
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def execute_query(self, query: str, params: Union[tuple, dict, None] = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return results as a list of dictionaries.
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            
        Returns:
            List of dictionaries containing the query results
        """
        if params is None:
            params = {}
            
        try:
            # Read operations can be executed on any node
            with self.get_connection(for_write=False) as conn:
                cursor = conn.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
                return results
        except sqlite3.Error as e:
            logger.error(f"Database query error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    def execute_update(self, query: str, params: Union[tuple, dict, None] = None) -> int:
        """
        Execute an update/insert/delete query and return affected rows.
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            
        Returns:
            Number of rows affected
        """
        if params is None:
            params = {}
            
        try:
            # Write operations must be executed on primary node
            with self.get_connection(for_write=True) as conn:
                cursor = conn.execute(query, params)
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Database update error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    def execute_script(self, script: str) -> None:
        """
        Execute a SQL script.
        
        Args:
            script: SQL script to execute
        """
        try:
            # Script execution is a write operation
            with self.get_connection(for_write=True) as conn:
                conn.executescript(script)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database script error: {e}")
            logger.error(f"Script: {script}")
            raise

# Global connection instance
db = DatabaseConnection() 