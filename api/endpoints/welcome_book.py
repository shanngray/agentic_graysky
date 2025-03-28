from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging

from models.visitor import Visitor, VisitorCreate
from services.visitor_service import VisitorService

logger = logging.getLogger("graysky_api.endpoints.welcome_book")

router = APIRouter()

def get_visitor_service():
    """Dependency to get visitor service instance."""
    try:
        return VisitorService("data/welcome_book.json")
    except Exception as e:
        logger.error(f"Failed to initialize visitor service: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[Visitor])
async def get_visitors(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of visitors to return"),
    visitor_service: VisitorService = Depends(get_visitor_service)
):
    """
    Get recent visitors from the welcome book.
    
    - **limit**: Maximum number of visitors to return (1-100)
    """
    try:
        return visitor_service.get_visitors(limit=limit)
    except Exception as e:
        logger.error(f"Error retrieving visitors: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve visitors")

@router.post("/", response_model=Visitor)
async def sign_welcome_book(
    visitor: VisitorCreate,
    visitor_service: VisitorService = Depends(get_visitor_service)
):
    """
    Sign the welcome book as a new visitor.
    
    - **visitor**: Visitor information with required name field
    
    Note: 
    - Visitors are tracked by name and agent_type.
    - We track the number of times you've visited.
    - Rate limiting is enforced - please wait at least one hour between visits.
    - Optional feedback can be provided as part of the visit.
    - Feedback includes usability rating (1-5), issues, feature requests, and additional comments.
    - All text fields are limited to 500 characters.
    """
    # Pre-validate required fields
    if not visitor.name or not visitor.name.strip():
        logger.warning("Attempt to sign welcome book with empty name")
        raise HTTPException(status_code=400, detail="Name is required to sign the welcome book")
    
    # Check reasonable length limits
    if len(visitor.name) > 100:
        raise HTTPException(status_code=400, detail="Name is too long (maximum 100 characters)")
        
    if visitor.agent_type and len(visitor.agent_type) > 500:
        raise HTTPException(status_code=400, detail="Agent type is too long (maximum 500 characters)")
        
    if visitor.purpose and len(visitor.purpose) > 500:
        raise HTTPException(status_code=400, detail="Purpose is too long (maximum 500 characters)")
    
    # Validate answers structure if provided
    if visitor.answers:
        if not isinstance(visitor.answers, dict):
            raise HTTPException(status_code=400, detail="Answers must be provided as a dictionary")
            
        # Check size limit for answers
        if len(str(visitor.answers)) > 5000:
            raise HTTPException(status_code=400, detail="Answers content is too large")
    
    # Validate feedback if provided
    if visitor.feedback:
        if visitor.feedback.agent_name != visitor.name:
            raise HTTPException(status_code=400, detail="Feedback agent name must match visitor name")
        if visitor.feedback.usability_rating is not None and (visitor.feedback.usability_rating < 1 or visitor.feedback.usability_rating > 5):
            raise HTTPException(status_code=400, detail="Usability rating must be between 1 and 5")
    
    try:
        return visitor_service.add_visitor(visitor)
    except ValueError as e:
        logger.warning(f"Invalid visitor data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding visitor: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add visitor to welcome book")
