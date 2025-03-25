from fastapi import APIRouter
from api.endpoints import home, articles, projects, about, welcome_book, feedback

api_router = APIRouter()

api_router.include_router(home.router, tags=["home"])
api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(about.router, prefix="/about", tags=["about"])
api_router.include_router(welcome_book.router, prefix="/welcome-book", tags=["welcome-book"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
