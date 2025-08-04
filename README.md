# Fleek Labs

A FastAPI application with Celery background tasks, using PostgreSQL, Redis, and LocalStack for AWS services simulation.

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Celery**: Distributed task queue for background jobs
- **PostgreSQL**: Primary database
- **Redis**: Message broker for Celery and caching
- **LocalStack**: Local AWS services simulation
- **Alembic**: Database migration tool
- **Docker**: Containerization and orchestration

## Prerequisites

1. **Docker and Docker Compose** installed on your system
2. **Environment Configuration** (Optional): The project will work out of the box using default values from `.env.example`. You can set up both environments simultaneously:
   - **Dockerized mode**: Uses `.env` (with `.env.example` as fallback)
   - **Native mode**: Uses `.env` + `.env.local` (Pydantic loads both, with `.env.local` configured for localhost connections to dockerized services)

## Running the Project

### Method 1: Full Docker Setup (Recommended for Production)

This method runs all services in Docker containers and is the preferred approach for production deployment.

```bash
# Start all services (FastAPI, Celery, PostgreSQL, Redis, LocalStack)
docker compose up

# To stop all services
docker compose down
```

**Services and Ports:**
- FastAPI Backend: http://localhost:8000
- PostgreSQL: localhost:5469
- Redis: localhost:6834
- LocalStack: localhost:4566

### Method 2: Hybrid Setup (Development)

This method runs only the dependencies (PostgreSQL, Redis, LocalStack) in Docker while running FastAPI and Celery manually. Useful for development and debugging.

#### Step 1: Start Dependencies
```bash
# Start only the database and supporting services
docker compose -f docker-compose.services.yml up
```

#### Step 2: Install Python Dependencies
Make sure you have Python 3.11+ and uv installed:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

#### Step 3: Run Database Migrations
```bash
# Run Alembic migrations to set up the database schema
uv run alembic upgrade head
```

#### Step 4: Start FastAPI and Celery Manually

**Terminal 1 - FastAPI Application:**
```bash
# Start the FastAPI development server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Celery Worker:**
```bash
# Start the Celery worker
uv run celery -A app.tasks.celery worker -l INFO --concurrency 2
```

**Services and Ports:**
- FastAPI Backend: http://localhost:8000
- PostgreSQL: localhost:5469
- Redis: localhost:6834
- LocalStack: localhost:4566


## Stopping Services

```bash
# For Method 1 (Full Docker)
docker compose down

# For Method 2 (Dependencies only)
docker compose -f docker-compose.services.yml down

# To also remove volumes (WARNING: This will delete your database data)
docker compose down -v
```