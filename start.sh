#!/bin/bash
set -e

echo "Initializing database..."
python -c "from threads.models import init_db; init_db(); print('Database initialized successfully')"

echo "Starting Reflex app on port ${PORT:-8000}..."
exec reflex run --env prod --loglevel info
