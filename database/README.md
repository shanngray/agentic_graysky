# Database Module for Agentic Graysky

This module provides SQLite database functionality for the Agentic Graysky application.

## Architecture

The database module is structured as follows:

- `connection.py`: Database connection utilities and pooling
- `schema.py`: Database schema definitions and migrations
- `model.py`: Pydantic models for data validation and serialization
- `visitor_db.py`: Data access layer for visitors and answers tables
- `feedback_db.py`: Data access layer for feedback table
- `migration.py`: Utilities for importing data from JSON files
- `init_db.py`: Script to initialize the database and run migrations
- `tests/`: Test suite for database functionality

## Database Schema

### Visitors Table
Stores information about visitors to the website.

```sql
CREATE TABLE IF NOT EXISTS visitors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    agent_type TEXT,
    purpose TEXT,
    visit_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    visit_count INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT name_length CHECK(length(name) <= 100),
    CONSTRAINT agent_type_length CHECK(length(agent_type) <= 500),
    CONSTRAINT purpose_length CHECK(length(purpose) <= 500)
);
```

### Answers Table
Stores visitor answers as key-value pairs.

```sql
CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visitor_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    FOREIGN KEY (visitor_id) REFERENCES visitors(id) ON DELETE CASCADE,
    CONSTRAINT key_length CHECK(length(key) <= 50),
    CONSTRAINT value_length CHECK(length(value) <= 500)
);
```

### Feedback Table
Stores feedback submitted by visitors.

```sql
CREATE TABLE IF NOT EXISTS feedback (
    id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    agent_type TEXT,
    submission_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    issues TEXT,
    feature_requests TEXT,
    usability_rating INTEGER,
    additional_comments TEXT,
    CONSTRAINT agent_name_length CHECK(length(agent_name) <= 100),
    CONSTRAINT agent_type_length CHECK(length(agent_type) <= 500),
    CONSTRAINT issues_length CHECK(length(issues) <= 2000),
    CONSTRAINT feature_requests_length CHECK(length(feature_requests) <= 2000),
    CONSTRAINT additional_comments_length CHECK(length(additional_comments) <= 2000),
    CONSTRAINT usability_rating_range CHECK(usability_rating BETWEEN 1 AND 10)
);
```

## Usage

### Initializing the Database

To initialize the database:

```python
from database.init_db import setup_database

# Initialize with data migration from JSON files
setup_database(with_migration=True)

# Or initialize empty database
setup_database(with_migration=False)
```

### Working with Visitors

```python
from database.visitor_db import add_visitor, get_visitors, get_visitor_by_id

# Add a visitor
visitor = add_visitor(
    name="Visitor Name",
    agent_type="Agent Type",
    purpose="Purpose",
    answers={"question1": "answer1", "question2": "answer2"}
)

# Get all visitors
visitors = get_visitors(limit=10)

# Get visitor by ID
visitor = get_visitor_by_id(visitor_id)
```

### Working with Feedback

```python
from database.feedback_db import add_feedback, get_feedback

# Add feedback
feedback = add_feedback(
    agent_name="Agent Name",
    agent_type="Agent Type",
    issues="Issues",
    feature_requests="Feature Requests",
    usability_rating=8,
    additional_comments="Comments"
)

# Get all feedback
feedback_entries = get_feedback(limit=10)
```

## Running Tests

To run the database tests:

```bash
python -m unittest discover -s database/tests
```

## Migration from JSON Files

The system can import data from JSON files:

```python
from database.migration import migrate_all_data

# Migrate all data from JSON files
result = migrate_all_data()
print(f"Migrated {result['visitors']} visitors and {result['feedback']} feedback entries")
```

This is useful for transitioning from the previous JSON-based storage system.

## LiteFS Integration

This module now supports LiteFS for SQLite replication across multiple instances. LiteFS is a distributed file system that allows for replication of SQLite databases across multiple nodes.

### How LiteFS Works

LiteFS creates a distributed filesystem that replicates SQLite database files across multiple instances. Each instance mounts LiteFS, which intercepts file system operations to the database file. Write operations are only allowed on the primary node, while read operations can be performed on any node. Changes are automatically replicated from the primary to replicas.

### Configuration

LiteFS is configured using the `litefs.yml` file in the root directory. The configuration includes:

- FUSE mount point (`/var/lib/litefs`)
- Data directory for internal LiteFS storage (`/var/lib/litefs/data`)
- Primary election using Consul
- HTTP proxy for database access

### Local Development with LiteFS

For local development and testing with LiteFS:

```bash
# Start primary and replica nodes with docker-compose
docker-compose up

# In another terminal, test replication
python -m database.test_litefs
```

### Production Deployment with Fly.io

For production deployment on Fly.io:

1. Create a volume for database persistence:
   ```bash
   fly volumes create litefs_data --size 1
   ```

2. Deploy the application:
   ```bash
   fly deploy
   ```

3. Scale to multiple regions (replicas):
   ```bash
   fly regions add lhr
   ```

### DatabaseConnection Class Updates

The `DatabaseConnection` class has been updated to support LiteFS:

- Added `for_write` parameter to `get_connection()` to ensure write operations only happen on the primary
- Uses environment variables to detect LiteFS configuration
- Checks node role (primary/replica) before allowing write operations

### Environment Variables

The following environment variables are used:

- `LITEFS_DB_PATH`: Path to the SQLite database file within the LiteFS mount
- `LITEFS_MOUNTED`: Indicates whether LiteFS is mounted
- `LITEFS_PRIMARY`: Indicates whether the node is the primary (true/false) 