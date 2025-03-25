import os
import json
import frontmatter
import markdown
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from models.content import Article, Project

logger = logging.getLogger("graysky_api.content")

class ContentService:
    def __init__(self, content_dir: str = None):
        # Hardcode the relative path between projects
        if content_dir is None or not os.path.exists(content_dir):
            # Calculate the path: go up from current project, then to grayspace/src/app
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Get agentic_graysky dir
            parent_dir = os.path.dirname(current_dir)  # Get AI_projects dir
            content_dir = os.path.join(parent_dir, "grayspace", "src", "app")
        
        self.content_dir = Path(content_dir).resolve()
        # Validate that content directory exists
        if not self.content_dir.exists() or not self.content_dir.is_dir():
            logger.error(f"Content directory not found: {self.content_dir}")
            raise ValueError(f"Content directory not found: {self.content_dir}")
            
        # Define safe base paths to prevent path traversal
        self.articles_path = self.content_dir / 'articles'
        self.projects_path = self.content_dir / 'projects'
        
        # Directories to skip when scanning content
        self.skip_dirs = ['all', 'categories', '.git', 'node_modules']
        
    def _is_safe_path(self, path: Path) -> bool:
        """Check if a path is safe to access (within content directory)."""
        try:
            # Resolve to absolute path with symlinks resolved
            resolved_path = path.resolve()
            # Check if it's within the content directory
            return (
                resolved_path.exists() and 
                str(resolved_path).startswith(str(self.content_dir))
            )
        except (ValueError, OSError):
            logger.warning(f"Unsafe path access attempt: {path}")
            return False
        
    def _read_markdown_file(self, file_path: Path) -> Dict[str, Any]:
        """Read and parse a markdown file with frontmatter."""
        if not self._is_safe_path(file_path):
            logger.warning(f"Attempted to access file outside content directory: {file_path}")
            raise ValueError("Invalid file path")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                
            content = markdown.markdown(post.content, extensions=['markdown.extensions.extra'])
            
            metadata = post.metadata
            slug = file_path.parent.name
            
            return {
                "slug": slug,
                "content": content,
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"Error reading markdown file {file_path}: {str(e)}")
            raise
    
    def get_articles(self, category: Optional[str] = None, limit: int = 10) -> List[Article]:
        """Get articles, optionally filtered by category."""
        # Validate parameters
        if not self.articles_path.exists():
            logger.warning(f"Articles directory not found: {self.articles_path}")
            return []
            
        # Ensure limit is reasonable
        limit = min(max(1, limit), 50)  # Between 1 and 50
        
        # Sanitize category if provided
        if category:
            # Only allow alphanumeric and hyphen in category
            if not all(c.isalnum() or c == '-' for c in category):
                logger.warning(f"Invalid category format: {category}")
                return []
        
        articles = []
        
        try:
            # Get directories that represent articles
            for article_dir in self.articles_path.iterdir():
                # Skip non-directories and special directories
                if not article_dir.is_dir() or article_dir.name in self.skip_dirs or article_dir.name.startswith('.'):
                    continue
                    
                # Find the markdown file(s)
                md_files = list(article_dir.glob('*.md'))
                if not md_files:
                    continue
                    
                # Use the most relevant markdown file
                main_md_file = next((f for f in md_files if f.name == f"{article_dir.name}.md"), md_files[0])
                
                try:
                    article_data = self._read_markdown_file(main_md_file)
                    metadata = article_data['metadata']
                    
                    # Extract article category if available
                    article_category = metadata.get('category', None)
                    
                    # Skip if category filter is applied and doesn't match
                    if category and article_category != category:
                        continue
                        
                    articles.append(Article(
                        title=metadata.get('title', main_md_file.name.replace('.md', '')),
                        slug=article_data['slug'],
                        content=article_data['content'],
                        date=datetime.fromisoformat(metadata.get('date', datetime.now().isoformat())),
                        category=article_category,
                        tags=metadata.get('tags', []),
                        summary=metadata.get('summary', None)
                    ))
                except Exception as e:
                    logger.error(f"Error processing article {article_dir.name}: {str(e)}")
                    continue
        
            # Sort by date (newest first) and apply limit
            articles.sort(key=lambda x: x.date, reverse=True)
            return articles[:limit]
            
        except Exception as e:
            logger.error(f"Error scanning articles: {str(e)}")
            return []
    
    def get_article(self, slug: str) -> Optional[Article]:
        """Get a specific article by slug."""
        # Validate slug format to prevent path traversal
        if not slug or not all(c.isalnum() or c in ['-', '_'] for c in slug):
            logger.warning(f"Invalid slug format: {slug}")
            return None
            
        article_path = self.articles_path / slug
        
        if not self._is_safe_path(article_path) or not article_path.exists():
            return None
            
        try:
            md_files = list(article_path.glob('*.md'))
            if not md_files:
                return None
                
            main_md_file = next((f for f in md_files if f.name == f"{slug}.md"), md_files[0])
            
            article_data = self._read_markdown_file(main_md_file)
            metadata = article_data['metadata']
            
            return Article(
                title=metadata.get('title', main_md_file.name.replace('.md', '')),
                slug=article_data['slug'],
                content=article_data['content'],
                date=datetime.fromisoformat(metadata.get('date', datetime.now().isoformat())),
                category=metadata.get('category', None),
                tags=metadata.get('tags', []),
                summary=metadata.get('summary', None)
            )
        except Exception as e:
            logger.error(f"Error retrieving article {slug}: {str(e)}")
            return None
    
    def get_projects(self, limit: int = 10) -> List[Project]:
        """Get projects."""
        if not self.projects_path.exists():
            logger.warning(f"Projects directory not found: {self.projects_path}")
            return []
            
        # Ensure limit is reasonable
        limit = min(max(1, limit), 50)  # Between 1 and 50
        
        projects = []
        
        try:
            # Get directories that represent projects
            for project_dir in self.projects_path.iterdir():
                # Skip non-directories and special directories
                if not project_dir.is_dir() or project_dir.name in self.skip_dirs or project_dir.name.startswith('.'):
                    continue
                    
                # Find the markdown file(s)
                md_files = list(project_dir.glob('*.md'))
                if not md_files:
                    continue
                    
                # Use the most relevant markdown file
                main_md_file = next((f for f in md_files if f.name == f"{project_dir.name}.md"), md_files[0])
                
                try:
                    project_data = self._read_markdown_file(main_md_file)
                    metadata = project_data['metadata']
                    
                    projects.append(Project(
                        title=metadata.get('title', main_md_file.name.replace('.md', '')),
                        slug=project_data['slug'],
                        content=project_data['content'],
                        status=metadata.get('status', None),
                        technologies=metadata.get('technologies', []),
                        github_url=metadata.get('github_url', None),
                        demo_url=metadata.get('demo_url', None)
                    ))
                except Exception as e:
                    logger.error(f"Error processing project {project_dir.name}: {str(e)}")
                    continue
        
            return projects[:limit]
            
        except Exception as e:
            logger.error(f"Error scanning projects: {str(e)}")
            return []
    
    def get_project(self, slug: str) -> Optional[Project]:
        """Get a specific project by slug."""
        # Validate slug format to prevent path traversal
        if not slug or not all(c.isalnum() or c in ['-', '_'] for c in slug):
            logger.warning(f"Invalid slug format: {slug}")
            return None
            
        project_path = self.projects_path / slug
        
        if not self._is_safe_path(project_path) or not project_path.exists():
            return None
            
        try:
            md_files = list(project_path.glob('*.md'))
            if not md_files:
                return None
                
            main_md_file = next((f for f in md_files if f.name == f"{slug}.md"), md_files[0])
            
            project_data = self._read_markdown_file(main_md_file)
            metadata = project_data['metadata']
            
            return Project(
                title=metadata.get('title', main_md_file.name.replace('.md', '')),
                slug=project_data['slug'],
                content=project_data['content'],
                status=metadata.get('status', None),
                technologies=metadata.get('technologies', []),
                github_url=metadata.get('github_url', None),
                demo_url=metadata.get('demo_url', None)
            )
        except Exception as e:
            logger.error(f"Error retrieving project {slug}: {str(e)}")
            return None
