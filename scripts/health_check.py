#!/usr/bin/env python3
"""
Standalone health check script for the Agentic Graysky API.
Can be run against any deployment environment.
"""

import requests
import json
import sys
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("health_check")

def check_health(url, output_format="text"):
    """
    Check the health of a deployed API instance.
    
    Args:
        url: Base URL of the API
        output_format: Output format (text, json)
        
    Returns:
        int: 0 if healthy, 1 if unhealthy
    """
    # Ensure URL has no trailing slash
    base_url = url.rstrip('/')
    health_url = f"{base_url}/health"
    
    try:
        logger.info(f"Checking health at: {health_url}")
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            status = health_data.get("status", "unknown")
            
            if output_format == "json":
                print(json.dumps(health_data, indent=2))
            else:
                print(f"Health Status: {status}")
                print(f"Version: {health_data.get('version', 'unknown')}")
                print(f"Uptime: {health_data.get('uptime', 'unknown')}")
                
                # Database status
                db_status = health_data.get("database", {}).get("status", "unknown")
                print(f"Database: {db_status}")
                
                # LiteFS status
                if "litefs" in health_data:
                    litefs_status = health_data["litefs"].get("status", "unknown")
                    litefs_role = health_data["litefs"].get("role", "unknown")
                    print(f"LiteFS: {litefs_status} (role: {litefs_role})")
                
                # System metrics
                if "system" in health_data:
                    system = health_data["system"]
                    print(f"Memory Usage: {system.get('memory_usage', {}).get('percent', 0)}%")
                    print(f"CPU Usage: {system.get('cpu_percent', 0)}%")
            
            # Return success if status is healthy
            return 0 if status == "healthy" else 1
        else:
            logger.error(f"Health check failed with status code: {response.status_code}")
            print(f"Health check failed: HTTP {response.status_code}")
            if output_format == "json":
                print(json.dumps({"error": f"HTTP {response.status_code}", "body": response.text}))
            else:
                print(f"Response: {response.text}")
            return 1
    
    except requests.RequestException as e:
        logger.error(f"Error connecting to API: {e}")
        print(f"Error connecting to API: {e}")
        if output_format == "json":
            print(json.dumps({"error": str(e)}))
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Health check for Agentic Graysky API")
    parser.add_argument(
        "--url", 
        type=str,
        default="https://agentic-graysky.fly.dev",
        help="Base URL of the API"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    # Run health check
    exit_code = check_health(args.url, args.format)
    sys.exit(exit_code) 