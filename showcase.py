#!/usr/bin/env python3
import argparse
import requests
import json
import sys
from datetime import datetime
from tabulate import tabulate
import time

BASE_URL = "http://localhost:8000"

def display_response(response, title):
    """Format and display a response."""
    print(f"\n{title}")
    print("=" * 80)
    
    status_code = response.status_code
    status_text = "SUCCESS" if 200 <= status_code < 300 else "ERROR"
    
    print(f"Status: {status_code} ({status_text})")
    
    try:
        data = response.json()
        print("\nResponse:")
        print(json.dumps(data, indent=2))
    except:
        print("\nResponse (non-JSON):")
        print(response.text)
    
    print("=" * 80)

def showcase_welcome_book():
    """Showcase welcome book endpoints."""
    print("\nSHOWCASE: Welcome Book Endpoints")
    print("=" * 80)
    
    # GET endpoint
    print("1. Getting recent visitors...")
    response = requests.get(f"{BASE_URL}/welcome-book")
    display_response(response, "GET /welcome-book")
    
    # POST endpoint
    visitor_data = {
        "name": f"Showcase Bot {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "agent_type": "Showcase Utility",
        "purpose": "Demonstrating API functionality",
        "answers": {
            "favorite_feature": "The comprehensive API design",
            "suggestions": "Keep up the good work!"
        }
    }
    
    print("\n2. Signing the welcome book...")
    response = requests.post(f"{BASE_URL}/welcome-book", json=visitor_data)
    display_response(response, "POST /welcome-book")
    
    # Rate limiting demonstration
    print("\n3. Demonstrating rate limiting (should fail)...")
    second_response = requests.post(f"{BASE_URL}/welcome-book", json=visitor_data)
    display_response(second_response, "POST /welcome-book (Rate Limited)")

def showcase_feedback():
    """Showcase feedback endpoints."""
    print("\nSHOWCASE: Feedback Endpoints")
    print("=" * 80)
    
    # GET endpoint
    print("1. Getting recent feedback...")
    response = requests.get(f"{BASE_URL}/feedback")
    display_response(response, "GET /feedback")
    
    # POST endpoint
    feedback_data = {
        "agent_name": f"Showcase Bot {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "agent_type": "Showcase Utility",
        "issues": "No issues found during testing",
        "feature_requests": "Consider adding more detailed analytics",
        "usability_rating": 9,
        "additional_comments": "The API is well-designed and documented"
    }
    
    print("\n2. Submitting feedback...")
    response = requests.post(f"{BASE_URL}/feedback", json=feedback_data)
    display_response(response, "POST /feedback")

def showcase_content_endpoints():
    """Showcase content endpoints."""
    print("\nSHOWCASE: Content Endpoints")
    print("=" * 80)
    
    endpoints = [
        {"path": "/", "name": "Home Page"},
        {"path": "/about", "name": "About Page"},
        {"path": "/articles", "name": "Articles List"},
        {"path": "/projects", "name": "Projects List"}
    ]
    
    for endpoint in endpoints:
        print(f"\nAccessing {endpoint['name']}...")
        response = requests.get(f"{BASE_URL}{endpoint['path']}")
        display_response(response, f"GET {endpoint['path']}")
        time.sleep(1)  # Small delay to not flood the output

def main():
    parser = argparse.ArgumentParser(description='Graysky Agent API Showcase Utility')
    
    parser.add_argument('--welcome', action='store_true', help='Showcase welcome book endpoints')
    parser.add_argument('--feedback', action='store_true', help='Showcase feedback endpoints')
    parser.add_argument('--content', action='store_true', help='Showcase content endpoints')
    parser.add_argument('--all', action='store_true', help='Showcase all endpoints')
    parser.add_argument('--base-url', type=str, help='Base URL for API (default: http://localhost:8000)')
    
    args = parser.parse_args()
    
    # Set base URL if provided
    global BASE_URL
    if args.base_url:
        BASE_URL = args.base_url
    
    # Start the API server
    print(f"Connecting to API at {BASE_URL}")
    print("Make sure the API server is running with 'python main.py' in another terminal")
    
    try:
        # Check if server is running
        requests.get(f"{BASE_URL}/").raise_for_status()
    except requests.exceptions.RequestException:
        print(f"ERROR: Could not connect to API at {BASE_URL}")
        print("Please make sure the API server is running")
        sys.exit(1)
    
    # Show welcome message
    print("\nGraysky Agent API Showcase Utility")
    print("=" * 80)
    print("This utility demonstrates the functionality of the Graysky Agent API.")
    print("It will make real requests to the API endpoints and display the responses.")
    
    # Run the showcase based on arguments
    if args.all or (not args.welcome and not args.feedback and not args.content):
        showcase_welcome_book()
        showcase_feedback()
        showcase_content_endpoints()
    else:
        if args.welcome:
            showcase_welcome_book()
        if args.feedback:
            showcase_feedback()
        if args.content:
            showcase_content_endpoints()
    
    print("\nShowcase complete!")

if __name__ == "__main__":
    main() 