"""
Script to test LiteFS replication for the Agentic Graysky application.
This script demonstrates write operations on the primary and read operations on replicas.
"""

import argparse
import logging
import sys
import uuid
import requests
import time
import pytest
import socket
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("graysky_api.database.test_litefs")

def is_port_open(host: str, port: int) -> bool:
    """
    Check if a port is open on a given host.
    
    Args:
        host: Host address
        port: Port number
        
    Returns:
        True if port is open, False otherwise
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def add_test_visitor(host: str, port: int) -> Dict[str, Any]:
    """
    Add a test visitor through the API on the primary node.
    
    Args:
        host: Host address
        port: Port number
        
    Returns:
        Dictionary with visitor data
    """
    visitor_id = str(uuid.uuid4())
    visitor_data = {
        "name": f"Test Visitor {visitor_id[:8]}",
        "agent_type": "LiteFS Test Agent",
        "purpose": "Testing LiteFS replication",
        "answers": {
            "question1": "Testing answer 1",
            "question2": "Testing answer 2"
        }
    }
    
    url = f"http://{host}:{port}/api/visitors"
    response = requests.post(url, json=visitor_data)
    
    if response.status_code != 200:
        logger.error(f"Failed to add visitor: {response.text}")
        raise Exception(f"API error: {response.status_code}")
        
    logger.info(f"Added test visitor with ID: {response.json().get('id')}")
    return response.json()

def verify_visitor_on_replica(host: str, port: int, visitor_id: str) -> bool:
    """
    Verify that a visitor exists on the replica node.
    
    Args:
        host: Host address
        port: Port number
        visitor_id: Visitor ID to check
        
    Returns:
        True if visitor exists on replica, False otherwise
    """
    # Wait a short time for replication to occur
    time.sleep(1)
    
    url = f"http://{host}:{port}/api/visitors/{visitor_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        logger.error(f"Failed to find visitor on replica: {response.text}")
        return False
        
    logger.info(f"Successfully verified visitor on replica: {visitor_id}")
    return True

@pytest.mark.parametrize(
    "primary_host,primary_port,replica_host,replica_port",
    [
        (
            os.environ.get("PRIMARY_HOST", "localhost"), 
            int(os.environ.get("PRIMARY_PORT", "8080")),
            os.environ.get("REPLICA_HOST", "localhost"), 
            int(os.environ.get("REPLICA_PORT", "8081"))
        ),
    ]
)
@pytest.mark.skipif(os.environ.get("ENABLE_LITEFS_TEST", "false").lower() != "true",
                   reason="LiteFS replication test is disabled. Set ENABLE_LITEFS_TEST=true to enable.")
def test_litefs_replication(primary_host: str, primary_port: int, 
                           replica_host: str, replica_port: int) -> None:
    """
    Test LiteFS replication by writing to primary and reading from replica.
    
    Args:
        primary_host: Primary node host
        primary_port: Primary node port
        replica_host: Replica node host
        replica_port: Replica node port
    """
    # Check if the primary and replica servers are available
    primary_available = is_port_open(primary_host, primary_port)
    replica_available = is_port_open(replica_host, replica_port)
    
    if not primary_available or not replica_available:
        servers_status = []
        if not primary_available:
            servers_status.append(f"primary server at {primary_host}:{primary_port}")
        if not replica_available:
            servers_status.append(f"replica server at {replica_host}:{replica_port}")
            
        pytest.skip(f"Skipping test because required servers are not available: {', '.join(servers_status)}")
    
    try:
        logger.info(f"Testing LiteFS replication from {primary_host}:{primary_port} to {replica_host}:{replica_port}...")
        
        # Add a visitor on the primary
        visitor = add_test_visitor(primary_host, primary_port)
        visitor_id = visitor.get("id")
        
        if not visitor_id:
            logger.error("Failed to get visitor ID from response")
            pytest.fail("Failed to get visitor ID from response")
            
        # Verify the visitor exists on the replica
        success = verify_visitor_on_replica(replica_host, replica_port, visitor_id)
        
        if success:
            logger.info("LiteFS replication test successful: Data written to primary is visible on replica")
        else:
            logger.error("LiteFS replication test failed: Data not properly replicated")
            pytest.fail("LiteFS replication test failed: Data not properly replicated")
            
    except Exception as e:
        logger.error(f"Error testing LiteFS replication: {e}")
        pytest.fail(f"Error testing LiteFS replication: {e}")

# Keep the command-line interface for manual testing
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test LiteFS replication")
    parser.add_argument(
        "--primary-host", 
        default="localhost",
        help="Primary node host"
    )
    parser.add_argument(
        "--primary-port", 
        type=int,
        default=8080,
        help="Primary node port"
    )
    parser.add_argument(
        "--replica-host", 
        default="localhost",
        help="Replica node host"
    )
    parser.add_argument(
        "--replica-port", 
        type=int,
        default=8081,
        help="Replica node port"
    )
    args = parser.parse_args()
    
    # Run replication test
    test_litefs_replication(
        args.primary_host, 
        args.primary_port,
        args.replica_host, 
        args.replica_port
    ) 