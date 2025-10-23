#!/bin/bash
set -e

echo "Initializing database..."
python -c "from threads.models import init_db; init_db(); print('Database initialized successfully')"

echo "Starting Reflex app..."
exec reflex run --env prod --frontend-only
