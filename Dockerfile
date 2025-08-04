# Stage 1: Build stage
FROM python:3.12-alpine AS builder
COPY --from=ghcr.io/astral-sh/uv:0.5.23 /uv /uvx /bin/

WORKDIR /app

#COPY README.md README.md

# Install necessary build tools
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable


# Stage 2: Runtime stage
FROM python:3.12.3-alpine

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

WORKDIR /app
COPY . /app/
# Set entrypoint
RUN chmod +x ./scripts/*.sh

ENTRYPOINT ["./scripts/run-app.sh"]
