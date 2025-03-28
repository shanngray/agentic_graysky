"""
Pydantic models for database entities.
These models are used for data validation, serialization, and API contracts.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


class VisitorBase(BaseModel):
    """Base visitor model with common fields."""
    name: str = Field(..., max_length=100, description="Visitor's name")
    agent_type: Optional[str] = Field(None, max_length=500, description="Visitor's agent type")
    purpose: Optional[str] = Field(None, max_length=500, description="Visitor's purpose")


class VisitorCreate(VisitorBase):
    """Model for creating a new visitor."""
    answers: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Visitor's answers to questions"
    )
    
    @field_validator('answers')
    @classmethod
    def check_answers(cls, v):
        """Validate the answers field."""
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError("Answers must be a dictionary")
        
        # Check key length
        for key in v:
            if len(key) > 50:
                raise ValueError(f"Answer key '{key[:10]}...' exceeds maximum length of 50 characters")
        
        return v


class Visitor(VisitorBase):
    """Complete visitor model with all fields."""
    id: str = Field(..., description="Unique visitor ID")
    visit_time: datetime = Field(..., description="Time of visit")
    visit_count: int = Field(1, ge=1, description="Number of times this visitor has visited")
    answers: Dict[str, Any] = Field(default={}, description="Visitor's answers to questions")
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackBase(BaseModel):
    """Base feedback model with common fields."""
    agent_name: str = Field(..., max_length=100, description="Agent's name")
    agent_type: Optional[str] = Field(None, max_length=500, description="Agent's type")


class FeedbackCreate(FeedbackBase):
    """Model for creating new feedback."""
    issues: Optional[str] = Field(None, max_length=2000, description="Reported issues")
    feature_requests: Optional[str] = Field(None, max_length=2000, description="Requested features")
    usability_rating: Optional[int] = Field(None, ge=1, le=10, description="Usability rating (1-10)")
    additional_comments: Optional[str] = Field(None, max_length=2000, description="Additional comments")


class Feedback(FeedbackBase):
    """Complete feedback model with all fields."""
    id: str = Field(..., description="Unique feedback ID")
    submission_time: datetime = Field(..., description="Time of submission")
    issues: Optional[str] = Field(None, description="Reported issues")
    feature_requests: Optional[str] = Field(None, description="Requested features")
    usability_rating: Optional[int] = Field(None, description="Usability rating (1-10)")
    additional_comments: Optional[str] = Field(None, description="Additional comments")
    
    model_config = ConfigDict(from_attributes=True) 