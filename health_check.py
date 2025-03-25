"""
Health check endpoint for monitoring the application status.
This file should be imported in main.py.
"""
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

health_router = APIRouter()

@health_router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint that returns 200 OK when the service is running.
    This is used by Fly.io to monitor the health of the application.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "healthy"}
    ) 