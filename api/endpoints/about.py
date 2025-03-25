from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def get_about():
    """
    Get information about Graysky.
    """
    return {
        "name": "Graysky.ai",
        "description": "Graysky specializes in AI agent technology research and implementation.",
        "mission": "To advance the field of agentic AI systems and provide accessible, understandable resources for developers and AI agents.",
        "team": [
            {
                "name": "Shann Gray",
                "role": "Founder"
                # Add other team members as needed
            }
        ],
        "contact": {
            "website": "https://graysky.ai",
            "email": "contact@graysky.ai"
        }
    }
