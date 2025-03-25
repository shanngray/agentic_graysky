import json
import argparse
from pathlib import Path
from datetime import datetime
from tabulate import tabulate
import os
import sys

def display_welcome_book(limit=None, show_answers=False):
    """Display welcome book entries."""
    welcome_book_path = Path("data/welcome_book.json")
    
    if not welcome_book_path.exists():
        print("No welcome book entries found.")
        return
    
    try:
        with open(welcome_book_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("Error: Welcome book file is corrupted.")
        return
    except Exception as e:
        print(f"Error: Failed to read welcome book: {str(e)}")
        return
    
    if not data:
        print("No welcome book entries found.")
        return
    
    # Sort by visit time (newest first)
    sorted_data = sorted(
        data, 
        key=lambda x: datetime.fromisoformat(x.get("visit_time", "2000-01-01T00:00:00")), 
        reverse=True
    )
    
    # Apply limit if specified
    if limit:
        sorted_data = sorted_data[:limit]
    
    if show_answers:
        headers = ["ID", "Name", "Agent Type", "Visit Time", "Visit Count", "Purpose", "Answers"]
        rows = [
            [
                entry.get("id", "N/A")[:8] + "...",
                entry.get("name", "N/A"),
                entry.get("agent_type", "N/A"),
                entry.get("visit_time", "N/A"),
                entry.get("visit_count", 1),
                entry.get("purpose", "N/A"),
                json.dumps(entry.get("answers", {}), indent=2)
            ]
            for entry in sorted_data
        ]
    else:
        headers = ["ID", "Name", "Agent Type", "Visit Time", "Visit Count", "Purpose"]
        rows = [
            [
                entry.get("id", "N/A")[:8] + "...",
                entry.get("name", "N/A"),
                entry.get("agent_type", "N/A"),
                entry.get("visit_time", "N/A"),
                entry.get("visit_count", 1),
                entry.get("purpose", "N/A")
            ]
            for entry in sorted_data
        ]
    
    print(tabulate(rows, headers=headers, tablefmt="pretty"))
    print(f"Total entries: {len(data)}")

def display_feedback(limit=None):
    """Display feedback entries."""
    feedback_path = Path("data/feedback.json")
    
    if not feedback_path.exists():
        print("No feedback entries found.")
        return
    
    try:
        with open(feedback_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("Error: Feedback file is corrupted.")
        return
    except Exception as e:
        print(f"Error: Failed to read feedback: {str(e)}")
        return
    
    if not data:
        print("No feedback entries found.")
        return
    
    # Sort by submission time (newest first)
    sorted_data = sorted(
        data, 
        key=lambda x: datetime.fromisoformat(x.get("submission_time", "2000-01-01T00:00:00")), 
        reverse=True
    )
    
    # Apply limit if specified
    if limit:
        sorted_data = sorted_data[:limit]
    
    headers = ["ID", "Agent Name", "Agent Type", "Submission Time", "Rating", "Issues", "Feature Requests"]
    rows = [
        [
            entry.get("id", "N/A")[:8] + "...",
            entry.get("agent_name", "N/A"),
            entry.get("agent_type", "N/A"),
            entry.get("submission_time", "N/A"),
            entry.get("usability_rating", "N/A"),
            (entry.get("issues", "N/A")[:30] + "...") if entry.get("issues") and len(entry.get("issues")) > 30 else entry.get("issues", "N/A"),
            (entry.get("feature_requests", "N/A")[:30] + "...") if entry.get("feature_requests") and len(entry.get("feature_requests")) > 30 else entry.get("feature_requests", "N/A")
        ]
        for entry in sorted_data
    ]
    
    print(tabulate(rows, headers=headers, tablefmt="pretty"))
    print(f"Total entries: {len(data)}")

def display_entry_detail(entry_id, data_type="welcome_book"):
    """Display detailed information for a specific entry."""
    if data_type == "welcome_book":
        file_path = Path("data/welcome_book.json")
        title = "Welcome Book Entry"
    elif data_type == "feedback":
        file_path = Path("data/feedback.json")
        title = "Feedback Entry"
    else:
        print(f"Invalid data type: {data_type}")
        return
    
    if not file_path.exists():
        print(f"No {data_type} entries found.")
        return
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {data_type} file is corrupted.")
        return
    except Exception as e:
        print(f"Error: Failed to read {data_type}: {str(e)}")
        return
    
    # Find entry with matching ID
    entry = next((item for item in data if item.get("id", "").startswith(entry_id)), None)
    
    if not entry:
        print(f"No {data_type} entry found with ID: {entry_id}")
        return
    
    print(f"\n{title} Details:")
    print("=" * 50)
    
    # Format entry data
    for key, value in entry.items():
        if key in ["answers", "feature_requests", "issues", "additional_comments"]:
            print(f"\n{key.capitalize()}:")
            print("-" * 50)
            if isinstance(value, dict):
                for k, v in value.items():
                    print(f"{k}: {v}")
            else:
                print(value)
        else:
            print(f"{key}: {value}")
    
    print("=" * 50)

def main():
    parser = argparse.ArgumentParser(description='Graysky Agent API Data Review Utility')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Welcome book command
    welcome_parser = subparsers.add_parser('welcome', help='View welcome book entries')
    welcome_parser.add_argument('-l', '--limit', type=int, help='Limit number of entries to display')
    welcome_parser.add_argument('-a', '--answers', action='store_true', help='Show answers in output')
    welcome_parser.add_argument('-d', '--detail', type=str, help='Show detailed information for specific entry ID')
    
    # Feedback command
    feedback_parser = subparsers.add_parser('feedback', help='View feedback entries')
    feedback_parser.add_argument('-l', '--limit', type=int, help='Limit number of entries to display')
    feedback_parser.add_argument('-d', '--detail', type=str, help='Show detailed information for specific entry ID')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'welcome':
        if args.detail:
            display_entry_detail(args.detail, "welcome_book")
        else:
            display_welcome_book(args.limit, args.answers)
    elif args.command == 'feedback':
        if args.detail:
            display_entry_detail(args.detail, "feedback")
        else:
            display_feedback(args.limit)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 