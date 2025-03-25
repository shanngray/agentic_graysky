from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from api.router import api_router
import uvicorn
import time
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from health_check import health_router
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api.log")
    ]
)
logger = logging.getLogger("graysky_api")

# Rate limiting middleware
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_limit=100, window_seconds=60):
        super().__init__(app)
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.clients = {}
        
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean up old records
        if client_ip in self.clients:
            self.clients[client_ip] = [t for t in self.clients[client_ip] 
                                      if current_time - t < self.window_seconds]
        else:
            self.clients[client_ip] = []
            
        # Check rate limit
        if len(self.clients[client_ip]) >= self.requests_limit:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"}
            )
            
        # Add current request timestamp
        self.clients[client_ip].append(current_time)
        
        return await call_next(request)

# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

# Create FastAPI app
app = FastAPI(
    title="Graysky Agent API",
    description="An API designed for AI agents to interact with the Graysky website content",
    version="1.0.0",
)

# Configure CORS - Restrict to specific origins in production
origins = [
    "http://localhost:3000",
    "https://graysky.ai",
    "https://api.graysky.ai",
    "https://agentic-graysky.fly.dev",
    "https://agents.graysky.ai"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Add rate limiting
app.add_middleware(RateLimitMiddleware, requests_limit=100, window_seconds=60)

# Add security headers
app.add_middleware(SecurityHeadersMiddleware)

# Add trusted host middleware in production
if not __debug__:  # Production mode
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=[
            "graysky.ai", 
            "api.graysky.ai", 
            "localhost",
            "agentic-graysky.fly.dev",
            "agents.graysky.ai"
        ]
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the detailed error
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Return a generic error message to the client
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

# Include API router
app.include_router(api_router)

# Include health check router
app.include_router(health_router)

if __name__ == "__main__":
    # Use environment variable for port, default to 8080 for Fly.io
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
