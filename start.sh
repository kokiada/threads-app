#!/bin/bash
set -e

echo "Initializing database..."
python -c "from threads.models import init_db; init_db(); print('Database initialized successfully')"

echo "Exporting frontend..."
reflex export --frontend-only --no-zip

echo "Starting Reflex backend on port ${PORT:-8000}..."
exec reflex run --env prod --loglevel info --backend-only --backend-host 0.0.0.0 --backend-port ${PORT:-8000}
