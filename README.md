# Fleek Labs Media Processing API

A scalable, asynchronous media processing API that leverages AI models for image generation. Built with FastAPI for
high-performance REST APIs and Celery for distributed task processing, with cloud storage integration via S3.

## Architecture Overview

### Core Components

- **API Layer**: FastAPI handles HTTP requests, validation, and routing with automatic OpenAPI documentation
- **Task Queue**: Celery manages asynchronous media generation jobs with Redis as the message broker
- **Storage**: PostgreSQL for metadata and job tracking, S3 (via LocalStack) for media file storage
- **AI Integration**: Abstracted MediaGeneratorModel interface for pluggable AI model providers (Replicate, etc.)

### Key Features

- **Asynchronous Processing**: Media generation handled via background jobs to prevent API timeouts
- **Scalable Architecture**: Horizontal scaling through Celery workers and async FastAPI
- **Job Tracking**: Real-time status updates and job history
- **Flexible Storage**: S3-compatible object storage with controlled access patterns
- **Model Agnostic**: Support for multiple AI model providers through abstracted interfaces

## Tech Stack

### Core Technologies

- **FastAPI**: High-performance async web framework with automatic OpenAPI documentation
- **Celery**: Distributed task queue for reliable background job processing
- **PostgreSQL**: ACID-compliant relational database for metadata and job tracking
- **Redis**: In-memory data store used as Celery's message broker and for caching

### Infrastructure & DevOps

- **Docker & Docker Compose**: Container orchestration for consistent development and deployment
- **LocalStack**: AWS service emulation for local S3 development
- **Alembic**: Database schema versioning and migration management
- **uv**: Fast Python package manager for dependency management

### Tech Choice Rationale

This stack provides:

- **Scalability**: Horizontal scaling via Celery workers and async FastAPI
- **Reliability**: Job persistence, retry mechanisms, and transactional guarantees
- **Developer Experience**: Type hints, automatic API docs, and local AWS simulation
- **Production Readiness**: Battle-tested components suitable for high-traffic deployments

## Prerequisites

- **Docker** and **Docker Compose** (required)
- **Python 3.11+** (for local development only)
- **uv** package manager (for local development only)

### Environment Configuration

The project includes sensible defaults in `.env` and will work without additional configuration. For custom settings:

- **Docker mode**: Uses `.env` file with default values
- **Local development**: Use `.env.local` to override settings for localhost connections to dockerized services

## Quick Start

### Option 1: Full Docker Setup (Recommended)

Run the entire stack in Docker containers:

```bash
# Start all services
docker compose up

# Access the API documentation
open http://localhost:8000/docs

# Stop services
docker compose down
```

### Option 2: Local Development Setup

Run infrastructure in Docker, application locally for faster iteration:

```bash
# 1. Start infrastructure services
docker compose -f docker-compose.services.yml up -d

# 2. Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install Python dependencies
uv sync

# 4. Initialize database
uv run alembic upgrade head

# 5. Start services (in separate terminals)
# Terminal 1: API server
uv run uvicorn app.main:app --reload

# Terminal 2: Celery worker
uv run celery -A app.tasks.celery worker -l INFO
```

## Service Endpoints

| Service           | URL/Port                   | Description                       |
|-------------------|----------------------------|-----------------------------------|
| API Documentation | http://localhost:8000/docs | Interactive OpenAPI documentation |
| API Base URL      | http://localhost:8000      | REST API endpoint                 |
| PostgreSQL        | localhost:5469             | Database connection               |
| Redis             | localhost:6834             | Cache and message broker          |
| LocalStack S3     | localhost:4566             | AWS S3 emulation                  |

## Development Workflow

### Database Migrations

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one version
uv run alembic downgrade -1
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_media.py
```

### Project Structure

```
.
├── app/
│   ├── core/              # Core configuration, database, and base classes
│   ├── logs/              # Logging infrastructure and database logging
│   ├── media/             # Media processing module
│   │   ├── api/           # Media API routes and schemas
│   │   └── tests/         # Media-specific tests
│   ├── media_generator/   # AI model integration and storage
│   │   ├── dummy_media_generator/  # Mock generator for testing
│   │   └── tests/         # Generator tests
│   ├── tasks/             # Celery configuration and async tasks
│   └── tools/             # Utility endpoints and health checks
├── alembic/               # Database migrations
│   └── versions/          # Migration history
├── scripts/               # Startup and initialization scripts
├── tests/                 # Generic tests config
├── docker-compose.yml     # Full stack configuration
├── docker-compose.services.yml  # Infrastructure-only configuration
└── pyproject.toml         # Project dependencies and configuration
```

### Cleanup

```bash
# Stop all services
docker compose down

# Remove all data (database, S3 files)
docker compose down -v

# Clean Docker system
docker system prune -a
```

## Design Decisions

### /media/status/{job_id} endpoint

The current design has `/media/status/{job_id}` return the complete media resource. While this works functionally, it
might be unexpected since:

- I would expect "status" endpoints to return lightweight status information
- The endpoint name suggests it's about status, but it returns full resource data

**Alternatives to consider:**

- **Option 1:** Use `/media/{resource_id}` for complete resources, `/media/status/{job_id}` for status only
- **Option 2:** Rename to `/media/jobs/{job_id}` to better reflect that it returns complete job results

The current approach works but could be more predictable for API consumers.

### MediaGeneratorModel

I ended up creating an interface, MediaGeneratorModel, that represents the replicate api. I never tested the real
integration but I believe that if it doesn't work out of the box, it should run fine with a few adjustments.

### media/content/{media_id} endpoint

I assumed that the S3 bucket wouldn't be public and that there would be a need to generate a pre-signed URL to access
the generated media. To avoid the relatively expensive pre-signed URL generation on every request, I implemented the
media/content/{media_id} endpoint.

This approach might not be suitable depending on the API consumer's needs. For example, it could result in worse
performance if the client needs to list all the generated images.

## Additional Resources

- **API Documentation**: Available at http://localhost:8000/docs when running
- **Task Requirements**: Review `./requirements.md` for detailed specifications
