from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from models.content import Project
from services.content_service import ContentService

router = APIRouter()
content_service = ContentService("src/app")  # Path to your Next.js app content

@router.get("/", response_model=List[Project])
async def get_projects(
    limit: int = Query(10, description="Maximum number of projects to return")
):
    """
    Get a list of projects.
    """
    return content_service.get_projects(limit=limit)

@router.get("/{slug}", response_model=Project)
async def get_project(slug: str):
    """
    Get a specific project by its slug.
    """
    project = content_service.get_project(slug)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with slug '{slug}' not found")
    return project
