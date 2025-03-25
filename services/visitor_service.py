import json
import os
import uuid
import re
import html
import fcntl
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from models.visitor import Visitor, VisitorCreate

class VisitorService:
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.data_path = Path(data_file)
        self._ensure_data_file_exists()
        
        # Maximum allowed length for text fields
        self.max_name_length = 100
        self.max_field_length = 500
        self.max_visitors = 1000  # Limit total stored visitors
    
    def _ensure_data_file_exists(self):
        """Ensure the data file exists, create if it doesn't."""
        data_dir = self.data_path.parent
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
            
        if not self.data_path.exists():
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def _sanitize_input(self, text: str) -> str:
        """Sanitize user input to prevent injection attacks."""
        if not text:
            return ""
            
        # Strip any potentially dangerous HTML/script tags
        sanitized = html.escape(text)
        
        # Restrict to reasonable length
        return sanitized[:self.max_field_length]
    
    def _validate_visitor(self, visitor: VisitorCreate) -> Dict[str, str]:
        """Validate visitor data and return any errors."""
        errors = {}
        
        # Check required fields
        if not visitor.name or not visitor.name.strip():
            errors["name"] = "Name is required"
        
        # Check length limits
        if visitor.name and len(visitor.name) > self.max_name_length:
            errors["name"] = f"Name must be less than {self.max_name_length} characters"
            
        if visitor.agent_type and len(visitor.agent_type) > self.max_field_length:
            errors["agent_type"] = f"Agent type must be less than {self.max_field_length} characters"
            
        if visitor.purpose and len(visitor.purpose) > self.max_field_length:
            errors["purpose"] = f"Purpose must be less than {self.max_field_length} characters"
        
        # Validate answer content if provided
        if visitor.answers:
            if not isinstance(visitor.answers, dict):
                errors["answers"] = "Answers must be a dictionary"
            elif len(json.dumps(visitor.answers)) > 2000:  # Limit overall size
                errors["answers"] = "Answers exceeded maximum allowed size"
                
        return errors
    
    def _load_data(self) -> List[Dict[str, Any]]:
        """Load visitor data from file with file locking."""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            # Acquire shared lock for reading
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                return json.load(f)
            finally:
                # Release the lock
                fcntl.flock(f, fcntl.LOCK_UN)
    
    def _save_data(self, data: List[Dict[str, Any]]):
        """Save visitor data to file with exclusive locking."""
        # Keep only the most recent visitors if we exceed the limit
        if len(data) > self.max_visitors:
            # Sort by visit time (convert to datetime for sorting)
            data.sort(key=lambda x: datetime.fromisoformat(x['visit_time']), reverse=True)
            # Keep only the most recent ones
            data = data[:self.max_visitors]
            
        with open(self.data_path, 'w', encoding='utf-8') as f:
            # Acquire exclusive lock for writing
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                json.dump(data, f, default=str, indent=2)
            finally:
                # Release the lock
                fcntl.flock(f, fcntl.LOCK_UN)
    
    def get_visitors(self, limit: int = 10) -> List[Visitor]:
        """Get recent visitors."""
        # Ensure limit is reasonable
        limit = min(max(1, limit), 100)  # Between 1 and 100
        
        data = self._load_data()
        
        # Convert to Visitor models and sort by visit time (most recent first)
        visitors = [
            Visitor(
                id=item['id'],
                name=item['name'],
                agent_type=item.get('agent_type'),
                purpose=item.get('purpose'),
                visit_time=datetime.fromisoformat(item['visit_time']),
                answers=item.get('answers', {})
            )
            for item in data
        ]
        
        visitors.sort(key=lambda x: x.visit_time, reverse=True)
        return visitors[:limit]
    
    def add_visitor(self, visitor: VisitorCreate) -> Visitor:
        """Add a new visitor to the welcome book."""
        # Validate input
        errors = self._validate_visitor(visitor)
        if errors:
            error_msg = "; ".join(f"{k}: {v}" for k, v in errors.items())
            raise ValueError(f"Invalid visitor data: {error_msg}")
        
        # Sanitize input fields
        sanitized_name = self._sanitize_input(visitor.name)
        sanitized_agent_type = self._sanitize_input(visitor.agent_type) if visitor.agent_type else None
        sanitized_purpose = self._sanitize_input(visitor.purpose) if visitor.purpose else None
        
        # Sanitize answers if present
        sanitized_answers = {}
        if visitor.answers:
            for key, value in visitor.answers.items():
                sanitized_key = self._sanitize_input(key)[:50]  # Limit key length
                sanitized_value = (
                    self._sanitize_input(value) if isinstance(value, str)
                    else value
                )
                sanitized_answers[sanitized_key] = sanitized_value
        
        # Load existing data
        data = self._load_data()
        
        # Check for rate limiting - visitors with same name within the past hour
        recent_visits = [
            item for item in data 
            if item['name'] == sanitized_name and 
            datetime.fromisoformat(item['visit_time']) > datetime.now() - timedelta(hours=1)
        ]
        
        if recent_visits:
            raise ValueError("Rate limit exceeded. Please wait at least one hour between visits.")
        
        # Check if this visitor has been here before (by name and agent_type)
        existing_visitor = next(
            (item for item in data 
             if item['name'] == sanitized_name and 
             item.get('agent_type') == sanitized_agent_type),
            None
        )
        
        visit_count = 1
        
        if existing_visitor:
            visit_count = existing_visitor.get('visit_count', 1) + 1
        
        visitor_id = str(uuid.uuid4())
        visit_time = datetime.now().isoformat()
        
        new_visitor = {
            "id": visitor_id,
            "name": sanitized_name,
            "agent_type": sanitized_agent_type,
            "purpose": sanitized_purpose,
            "visit_time": visit_time,
            "visit_count": visit_count,
            "answers": sanitized_answers or {}
        }
        
        data.append(new_visitor)
        self._save_data(data)
        
        return Visitor(
            id=visitor_id,
            name=sanitized_name,
            agent_type=sanitized_agent_type,
            purpose=sanitized_purpose,
            visit_time=datetime.fromisoformat(visit_time),
            visit_count=visit_count,
            answers=sanitized_answers or {}
        )
