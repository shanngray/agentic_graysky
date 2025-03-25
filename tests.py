import json
import os
import pytest
from fastapi.testclient import TestClient
from pathlib import Path

# Import main application
from main import app

# Create test client
client = TestClient(app)

# Ensure data directory exists for welcome book tests
def ensure_test_data_dir():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    return data_dir

# Create a test welcome book file
def setup_test_welcome_book():
    data_dir = ensure_test_data_dir()
    test_file = data_dir / "test_welcome_book.json"
    
    # Initialize with empty list if file doesn't exist
    if not test_file.exists():
        with open(test_file, "w") as f:
            json.dump([], f)
    
    return test_file

# Test the home endpoint
def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    
    # Verify key sections exist in response
    assert "info" in data
    assert "site_map" in data
    assert "agent_guidance" in data
    assert "_links" in data
    
    # Verify site info
    assert data["info"]["name"] == "Graysky Agent API"
    assert data["info"]["version"] == "1.0.0"

# Test the about endpoint
def test_about_endpoint():
    response = client.get("/about")
    assert response.status_code == 200
    data = response.json()
    
    # Verify key information
    assert "name" in data
    assert "description" in data
    assert "mission" in data
    assert "team" in data
    assert "contact" in data
    
    # Check specific values
    assert data["name"] == "Graysky.ai"
    assert "Graysky specializes in" in data["description"]

# Test the welcome book GET endpoint
def test_welcome_book_get():
    response = client.get("/welcome-book")
    assert response.status_code == 200
    data = response.json()
    
    # Should return a list (even if empty)
    assert isinstance(data, list)

# Test the welcome book POST endpoint
def test_welcome_book_post():
    # Test visitor data
    test_visitor = {
        "name": "Test Agent",
        "agent_type": "Test Suite",
        "purpose": "Testing API endpoints",
        "answers": {
            "model": "Test Framework",
            "purpose": "API verification",
            "preference": "Structured JSON"
        }
    }
    
    # Post to welcome book
    response = client.post("/welcome-book", json=test_visitor)
    assert response.status_code == 200
    data = response.json()
    
    # Verify response contains expected fields
    assert data["name"] == test_visitor["name"]
    assert data["agent_type"] == test_visitor["agent_type"]
    assert data["purpose"] == test_visitor["purpose"]
    assert "id" in data
    assert "visit_time" in data
    
    # Verify answers were saved
    assert data["answers"]["model"] == test_visitor["answers"]["model"]
    assert data["answers"]["purpose"] == test_visitor["answers"]["purpose"]

# Test the articles collection endpoint
def test_articles_endpoint():
    response = client.get("/articles")
    assert response.status_code == 200
    data = response.json()
    
    # Should return a list
    assert isinstance(data, list)
    
    # If we have articles, verify their structure
    if data:
        article = data[0]
        assert "title" in article
        assert "slug" in article
        assert "content" in article
        assert "date" in article

# Test the projects collection endpoint
def test_projects_endpoint():
    response = client.get("/projects")
    assert response.status_code == 200
    data = response.json()
    
    # Should return a list
    assert isinstance(data, list)
    
    # If we have projects, verify their structure
    if data:
        project = data[0]
        assert "title" in project
        assert "slug" in project
        assert "content" in project

# Test article limit query parameter
def test_articles_limit_parameter():
    # Request with limit=2
    response = client.get("/articles?limit=2")
    assert response.status_code == 200
    data = response.json()
    
    # Should respect the limit
    assert len(data) <= 2

# Test article category filter
def test_articles_category_filter():
    # Get all articles first
    all_response = client.get("/articles")
    all_data = all_response.json()
    
    # If we have articles with categories, test filtering
    if all_data and any("category" in article and article["category"] for article in all_data):
        # Find a category to test
        test_category = next(article["category"] for article in all_data if "category" in article and article["category"])
        
        # Test filtering by that category
        response = client.get(f"/articles?category={test_category}")
        assert response.status_code == 200
        data = response.json()
        
        # All returned articles should have the specified category
        for article in data:
            assert article["category"] == test_category

# Test error handling for non-existent article
def test_nonexistent_article():
    response = client.get("/articles/this-article-does-not-exist")
    assert response.status_code == 404
    data = response.json()
    
    # Should return error detail
    assert "detail" in data

# Test error handling for non-existent project
def test_nonexistent_project():
    response = client.get("/projects/this-project-does-not-exist")
    assert response.status_code == 404
    data = response.json()
    
    # Should return error detail
    assert "detail" in data

# Test welcome book validation - empty name
def test_welcome_book_validation():
    # Test visitor with empty name
    test_visitor = {
        "name": "",
        "agent_type": "Test Suite",
        "purpose": "Testing validation"
    }
    
    # Post to welcome book
    response = client.post("/welcome-book", json=test_visitor)
    assert response.status_code == 400
    data = response.json()
    
    # Should return validation error
    assert "detail" in data

# Test welcome book with missing fields
def test_welcome_book_missing_fields():
    # Test visitor with missing required fields
    test_visitor = {
        "agent_type": "Test Suite"
        # Name is missing
    }
    
    # Post to welcome book
    response = client.post("/welcome-book", json=test_visitor)
    assert response.status_code in [400, 422]  # Either validation or schema error

# Run all tests if file executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 