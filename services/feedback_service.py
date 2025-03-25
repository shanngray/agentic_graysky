import json
import os
import uuid
import html
import fcntl
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from models.visitor import Feedback, FeedbackCreate

class FeedbackService:
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.data_path = Path(data_file)
        self._ensure_data_file_exists()
        
        # Maximum allowed length for text fields
        self.max_name_length = 100
        self.max_field_length = 2000  # Longer limit for feedback text
        self.max_feedback_entries = 1000  # Limit total stored feedback entries
    
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
    
    def _validate_feedback(self, feedback: FeedbackCreate) -> Dict[str, str]:
        """Validate feedback data and return any errors."""
        errors = {}
        
        # Check required fields
        if not feedback.agent_name or not feedback.agent_name.strip():
            errors["agent_name"] = "Agent name is required"
        
        # Check length limits
        if feedback.agent_name and len(feedback.agent_name) > self.max_name_length:
            errors["agent_name"] = f"Agent name must be less than {self.max_name_length} characters"
            
        if feedback.agent_type and len(feedback.agent_type) > self.max_name_length:
            errors["agent_type"] = f"Agent type must be less than {self.max_name_length} characters"
            
        if feedback.issues and len(feedback.issues) > self.max_field_length:
            errors["issues"] = f"Issues text must be less than {self.max_field_length} characters"
            
        if feedback.feature_requests and len(feedback.feature_requests) > self.max_field_length:
            errors["feature_requests"] = f"Feature requests must be less than {self.max_field_length} characters"
            
        if feedback.additional_comments and len(feedback.additional_comments) > self.max_field_length:
            errors["additional_comments"] = f"Additional comments must be less than {self.max_field_length} characters"
            
        if feedback.usability_rating is not None and not (1 <= feedback.usability_rating <= 10):
            errors["usability_rating"] = "Usability rating must be between 1 and 10"
                
        return errors
    
    def _load_data(self) -> List[Dict[str, Any]]:
        """Load feedback data from file with file locking."""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            # Acquire shared lock for reading
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                return json.load(f)
            finally:
                # Release the lock
                fcntl.flock(f, fcntl.LOCK_UN)
    
    def _save_data(self, data: List[Dict[str, Any]]):
        """Save feedback data to file with exclusive locking."""
        # Keep only the most recent entries if we exceed the limit
        if len(data) > self.max_feedback_entries:
            # Sort by submission time (convert to datetime for sorting)
            data.sort(key=lambda x: datetime.fromisoformat(x['submission_time']), reverse=True)
            # Keep only the most recent ones
            data = data[:self.max_feedback_entries]
            
        with open(self.data_path, 'w', encoding='utf-8') as f:
            # Acquire exclusive lock for writing
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                json.dump(data, f, default=str, indent=2)
            finally:
                # Release the lock
                fcntl.flock(f, fcntl.LOCK_UN)
    
    def get_feedback(self, limit: int = 10) -> List[Feedback]:
        """Get recent feedback entries."""
        # Ensure limit is reasonable
        limit = min(max(1, limit), 100)  # Between 1 and 100
        
        data = self._load_data()
        
        # Convert to Feedback models and sort by submission time (most recent first)
        feedback_entries = [
            Feedback(
                id=item['id'],
                agent_name=item['agent_name'],
                agent_type=item.get('agent_type'),
                submission_time=datetime.fromisoformat(item['submission_time']),
                issues=item.get('issues'),
                feature_requests=item.get('feature_requests'),
                usability_rating=item.get('usability_rating'),
                additional_comments=item.get('additional_comments')
            )
            for item in data
        ]
        
        feedback_entries.sort(key=lambda x: x.submission_time, reverse=True)
        return feedback_entries[:limit]
    
    def add_feedback(self, feedback: FeedbackCreate) -> Feedback:
        """Add a new feedback entry."""
        # Validate input
        errors = self._validate_feedback(feedback)
        if errors:
            error_msg = "; ".join(f"{k}: {v}" for k, v in errors.items())
            raise ValueError(f"Invalid feedback data: {error_msg}")
        
        # Sanitize input fields
        sanitized_agent_name = self._sanitize_input(feedback.agent_name)
        sanitized_agent_type = self._sanitize_input(feedback.agent_type) if feedback.agent_type else None
        sanitized_issues = self._sanitize_input(feedback.issues) if feedback.issues else None
        sanitized_feature_requests = self._sanitize_input(feedback.feature_requests) if feedback.feature_requests else None
        sanitized_additional_comments = self._sanitize_input(feedback.additional_comments) if feedback.additional_comments else None
        
        # Load existing data
        data = self._load_data()
        
        feedback_id = str(uuid.uuid4())
        submission_time = datetime.now().isoformat()
        
        new_feedback = {
            "id": feedback_id,
            "agent_name": sanitized_agent_name,
            "agent_type": sanitized_agent_type,
            "submission_time": submission_time,
            "issues": sanitized_issues,
            "feature_requests": sanitized_feature_requests,
            "usability_rating": feedback.usability_rating,
            "additional_comments": sanitized_additional_comments
        }
        
        data.append(new_feedback)
        self._save_data(data)
        
        return Feedback(
            id=feedback_id,
            agent_name=sanitized_agent_name,
            agent_type=sanitized_agent_type,
            submission_time=datetime.fromisoformat(submission_time),
            issues=sanitized_issues,
            feature_requests=sanitized_feature_requests,
            usability_rating=feedback.usability_rating,
            additional_comments=sanitized_additional_comments
        ) 