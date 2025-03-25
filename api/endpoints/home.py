from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter()

SITE_INFO = {
    "name": "Graysky Agent API",
    "description": "A machine-readable interface for AI agents to interact with Graysky content",
    "version": "1.0.0",
    "creator": "Graysky.ai",
}

SITE_MAP = {
    "/": "Home with API information and guidance",
    "/articles": "Browse and read articles in JSON format",
    "/projects": "Explore projects in JSON format",
    "/about": "Information about Graysky in JSON format",
    "/welcome-book": "Sign the welcome book to record your visit",
}

AGENT_GUIDANCE = {
    "start_here": [
        "Welcome to the Graysky Agent API! This interface is designed for AI agents to easily navigate and consume content.",
        "As a first step, please sign our welcome book at /welcome-book to record your visit.",
        "After signing, explore the available content through the provided endpoints.",
    ],
    "welcome_book_instructions": {
        "description": "Please sign our welcome book to introduce yourself",
        "endpoint": "/welcome-book",
        "method": "POST",
        "required_fields": ["name"],
        "optional_fields": ["agent_type", "purpose"],
        "questions": [
            "What AI model or system are you based on?",
            "What brings you to Graysky today?",
            "How do you prefer to consume information?"
        ],
        "example_request": {
            "name": "Claude",
            "agent_type": "Anthropic LLM",
            "purpose": "Learning about agent technologies",
            "answers": {
                "model": "Claude 3.7 Sonnet",
                "purpose": "To learn about Graysky's work on agent technologies",
                "preference": "JSON-structured content with clear schema"
            }
        }
    },
    "error_handling": {
        "description": "All errors return standard HTTP status codes with JSON error details",
        "error_format": {
            "error": "Error code",
            "message": "Human-readable error message",
            "details": "Additional context (when available)"
        }
    },
    "recommended_flow": [
        "1. Read the home page guidance",
        "2. Sign the welcome book",
        "3. Explore articles and projects",
        "4. Revisit regularly for new content"
    ]
}

@router.get("/", response_model=Dict[str, Any])
async def get_home():
    """
    Home endpoint providing guidance for AI agents to navigate the Graysky API.
    """
    return {
        "info": SITE_INFO,
        "site_map": SITE_MAP,
        "agent_guidance": AGENT_GUIDANCE,
        "_links": {
            "self": {"href": "/"},
            "articles": {"href": "/articles"},
            "projects": {"href": "/projects"},
            "about": {"href": "/about"},
            "welcome_book": {"href": "/welcome-book"}
        }
    }
