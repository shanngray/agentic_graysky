from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from models.content import Article
from services.content_service import ContentService

router = APIRouter()
content_service = ContentService()  # Use default path (data/content)

@router.get("/", response_model=List[Article])
async def get_articles(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, description="Maximum number of articles to return")
):
    """
    Get a list of articles, optionally filtered by category.
    """
    return content_service.get_articles(category=category, limit=limit)

@router.get("/{slug}", response_model=Article)
async def get_article(slug: str):
    """
    Get a specific article by its slug.
    """
    article = content_service.get_article(slug)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article with slug '{slug}' not found")
    return article
