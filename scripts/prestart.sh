#!/bin/sh
set -e
set -x

python -m app.backend_pre_start

# Run migrations
python -m alembic upgrade head
