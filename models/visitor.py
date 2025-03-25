from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class VisitorBase(BaseModel):
    name: str
    agent_type: Optional[str] = None
    purpose: Optional[str] = None
    visit_count: Optional[int] = 1
    
class VisitorCreate(VisitorBase):
    answers: Optional[dict] = None
    
class Visitor(VisitorBase):
    id: str
    visit_time: datetime
    answers: dict
    
    model_config = ConfigDict(from_attributes=True)

class FeedbackBase(BaseModel):
    agent_name: str
    agent_type: Optional[str] = None
    
class FeedbackCreate(FeedbackBase):
    issues: Optional[str] = None
    feature_requests: Optional[str] = None
    usability_rating: Optional[int] = None
    additional_comments: Optional[str] = None
    
class Feedback(FeedbackBase):
    id: str
    submission_time: datetime
    issues: Optional[str] = None
    feature_requests: Optional[str] = None
    usability_rating: Optional[int] = None
    additional_comments: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
