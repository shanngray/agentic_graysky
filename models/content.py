from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ContentBase(BaseModel):
    title: str
    slug: str
    content: str
    
class Article(ContentBase):
    date: datetime
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    
class Project(ContentBase):
    status: Optional[str] = None
    technologies: Optional[List[str]] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
