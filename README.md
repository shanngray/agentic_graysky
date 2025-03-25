# Graysky Agent API

A FastAPI-based backend for AI agents to interact with the Graysky website content, featuring secure API design, rate limiting, and comprehensive documentation.

## Project Overview

The Graysky Agent API is designed to provide programmatic access to content and services on the Graysky website. It follows best practices for API design with a focus on security, rate limiting, and structured response formats that are optimized for AI agent consumption.

## Features

- **Content Access**: Retrieve articles and projects from the Graysky website
- **Visitor Tracking**: Record visitor information in a welcome book
- **Feedback Collection**: Gather feedback from AI agents or users
- **Security Measures**: Implements rate limiting, CORS protection, and security headers
- **AI-Agent Optimized**: Response formats designed for easy consumption by AI agents

## Installation

### Prerequisites

- Python 3.10 or higher
- uv (optional but recommended for dependency management)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/agentic_graysky.git
   cd agentic_graysky
   ```

2. Set up a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   
   Or with uv:
   ```
   uv pip install -r requirements.txt
   ```

## Usage

### Running the API Server

Start the main API server:

```
python main.py
```

The server will start on `http://localhost:8000` by default.

### Running the Demo Website

For testing purposes, you can also run the agentic website demo:

```
python agentic_website.py
```

### API Endpoints

#### Content Endpoints

- `GET /`: Home page content
- `GET /about`: About page content
- `GET /articles`: List of articles
- `GET /articles/{slug}`: Specific article content
- `GET /projects`: List of projects
- `GET /projects/{slug}`: Specific project content

#### Visitor Endpoints

- `GET /welcome-book`: List recent visitors
- `POST /welcome-book`: Sign the welcome book

#### Feedback Endpoints

- `GET /feedback`: List recent feedback
- `POST /feedback`: Submit feedback

### Showcase Utility

The project includes a showcase utility to demonstrate API functionality:

```
python showcase.py --all  # Run all demos
python showcase.py --welcome  # Demo welcome book endpoints
python showcase.py --feedback  # Demo feedback endpoints
python showcase.py --content  # Demo content endpoints
```

## Testing

Run the test suite:

```
python run_tests.py
```

Or directly with pytest:

```
pytest tests.py -v
```

## Project Structure

- `api/`: API routes and endpoint definitions
  - `endpoints/`: Individual endpoint handlers
  - `router.py`: Main API router
- `data/`: JSON data storage for visitors and feedback
- `models/`: Pydantic models for data validation
- `services/`: Business logic implementation
  - `content_service.py`: Handles content retrieval
  - `feedback_service.py`: Manages feedback
  - `visitor_service.py`: Handles visitor data
- `main.py`: FastAPI application entry point
- `agentic_website.py`: Demo website designed for AI agents
- `showcase.py`: Demonstration utility
- `tests.py`: Test suite
- `utils.py`: Utility functions

## Security

The project implements several security best practices:

- Rate limiting to prevent abuse
- Secure CORS configuration
- Security headers
- Path traversal prevention
- Input validation and sanitization
- Comprehensive error handling

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions to the Graysky Agent API are welcome. Please feel free to submit issues and pull requests.
