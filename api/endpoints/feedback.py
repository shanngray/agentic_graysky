from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging

from models.visitor import Feedback, FeedbackCreate
from services.feedback_service import FeedbackService

logger = logging.getLogger("graysky_api.endpoints.feedback")

router = APIRouter()

def get_feedback_service():
    """Dependency to get feedback service instance."""
    try:
        return FeedbackService("data/feedback.json")
    except Exception as e:
        logger.error(f"Failed to initialize feedback service: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[Feedback])
async def get_feedback(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of feedback entries to return"),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """
    Get recent feedback entries.
    
    - **limit**: Maximum number of feedback entries to return (1-100)
    """
    try:
        return feedback_service.get_feedback(limit=limit)
    except Exception as e:
        logger.error(f"Error retrieving feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve feedback")

@router.post("/", response_model=Feedback)
async def submit_feedback(
    feedback: FeedbackCreate,
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """
    Submit feedback about the website.
    
    - **feedback**: Feedback information with required agent_name field
    """
    # Pre-validate required fields
    if not feedback.agent_name or not feedback.agent_name.strip():
        logger.warning("Attempt to submit feedback with empty agent name")
        raise HTTPException(status_code=400, detail="Agent name is required to submit feedback")
    
    try:
        return feedback_service.add_feedback(feedback)
    except ValueError as e:
        logger.warning(f"Invalid feedback data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback") 