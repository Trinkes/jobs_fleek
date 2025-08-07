Overview

This assignment is designed to evaluate your skills and architectural approach as a Senior Backend Engineer / Architect. We expect you to apply best practices in Python, FastAPI, async architecture, and infrastructure design, with a clear focus on clean structure, maintainability, and reliability.

Task Description

Your task involves building a microservice that performs asynchronous media generation using the Replicate API, with the following features:

1. API Layer (FastAPI)
   Expose a POST /generate endpoint that accepts a prompt and generation parameters.

The endpoint should enqueue a job to an asynchronous task queue for background processing.

A GET /status/{job_id} endpoint should return the status and result (if available).

2. Async Job Queue
   Implement an asynchronous job queue using Celery with Redis/RabbitMQ, or Dramatiq, or similar.

Each job should:

Call the Replicate API (mocked or real).
Handle failures with automatic retries.
Store the resulting image persistently (e.g., S3-compatible storage or local FS).
Update job status in a persistent store (e.g., PostgreSQL).

3. Persistent Storage

Store the following in a database:

Job metadata (prompt, parameters, status, timestamps, retry attempts, etc.).

Path/URL of generated media.

Store the media files in either:

S3-compatible bucket (MinIO or actual S3), or
Local file system.

Requirements

Asynchronous Architecture: All external I/O (e.g., HTTP, file, DB) should be async-compatible.

Retries: Implement retry logic for failed jobs with exponential backoff.

Error Handling: Gracefully handle and persist errors.

Configuration: Use .env or similar config pattern for secrets and service URLs.

Reusability: Design components (e.g., job handler, media client) as reusable modules.

Clean Architecture: Apply principles of separation of concerns (API, services, tasks, models).

Bonus Points

Typed Pydantic models and response validation

Dockerized setup (e.g., with docker-compose)

Usage of Alembic for schema migrations

Async ORM (e.g., Tortoise ORM or SQLModel)

Submission Guidelines

GitHub Repository: Set up an open GitHub repository for your assignment and share it with atika@fleek.xyz

README.md: Include clear setup instructions, architecture overview, and tech choices.

If taking help from AI to complete the assignment, please also add your responses to the below questions:

1. Please share the exact sequence of prompts you used to generate this code
2. Please improve the code in accordance to the best practices, whatever you think they are.
3. Please share those best practices with us in bullet points and most importantly, please share a specific prompt you would you to target specific areas of the code for improvement - i.e. targeted improvement of specific files with specific functionality (i.e. do NOT ask AI to just "improve the code with best practices" that will again not show us anything that we need to see).

Let us know if you have any questions, thank you.
