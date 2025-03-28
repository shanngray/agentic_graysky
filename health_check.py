"""
Health check endpoint for monitoring the application status.
This file should be imported in main.py.
"""
from fastapi import APIRouter
from database.connection import get_connection
import psutil  # type: ignore
import platform
import time
import os
from datetime import datetime, timedelta
import sqlite3

health_router = APIRouter()

# Track when the application started
START_TIME = time.time()

@health_router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint that provides detailed information about the API status.
    
    Returns:
        dict: Health check information including version, database status, and system metrics
    """
    # Get database connection status
    db_status = check_database_connection()
    
    # Get LiteFS status if enabled
    litefs_status = check_litefs_status() if os.environ.get("LITEFS_MOUNTED") == "true" else {"enabled": False}
    
    # Get system metrics
    system_info = {
        "memory_usage": {
            "percent": psutil.virtual_memory().percent,
            "used_mb": psutil.virtual_memory().used / (1024 * 1024),
            "available_mb": psutil.virtual_memory().available / (1024 * 1024)
        },
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "platform": platform.platform(),
        "python_version": platform.python_version()
    }
    
    # Calculate uptime
    uptime_seconds = time.time() - START_TIME
    uptime = str(timedelta(seconds=int(uptime_seconds)))
    
    # Construct the health response
    health_data = {
        "status": "healthy" if db_status["status"] == "connected" else "unhealthy",
        "version": "1.0.0",  # Should match app version in main.py
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": uptime,
        "database": db_status,
        "system": system_info
    }
    
    # Add LiteFS status if enabled
    if litefs_status["enabled"]:
        health_data["litefs"] = litefs_status
    
    return health_data

def check_database_connection():
    """
    Check if the database connection is working.
    
    Returns:
        dict: Database connection status and metadata
    """
    try:
        # Get a database connection
        conn = get_connection()
        
        # Execute a simple query to verify connection
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            
            # Get database file info
            cursor.execute("PRAGMA database_list")
            db_info = cursor.fetchall()
            db_path = next((info[2] for info in db_info if info[1] == 'main'), 'Unknown')
            
            # Get database size
            db_size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0
            db_size_mb = db_size_bytes / (1024 * 1024)
            
        return {
            "status": "connected",
            "version": version,
            "path": db_path,
            "size_mb": round(db_size_mb, 2)
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e)
        }

def check_litefs_status():
    """
    Check the status of LiteFS if enabled.
    
    Returns:
        dict: LiteFS status information
    """
    litefs_status = {"enabled": True}
    
    try:
        # Check if this instance is primary or replica
        if os.path.exists("/var/lib/litefs/primary"):
            role = "primary"
        else:
            role = "replica"
        
        litefs_status["role"] = role
        litefs_status["status"] = "running"
        
        # Check mount directory
        litefs_db_path = os.environ.get("LITEFS_DB_PATH", "/var/lib/litefs/data/graysky.db")
        if os.path.exists(litefs_db_path):
            litefs_status["db_path"] = litefs_db_path
            litefs_status["db_size_mb"] = round(os.path.getsize(litefs_db_path) / (1024 * 1024), 2)
        else:
            litefs_status["status"] = "warning"
            litefs_status["message"] = "Database file not found at expected path"
    
    except Exception as e:
        litefs_status["status"] = "error"
        litefs_status["error"] = str(e)
    
    return litefs_status 