#!/bin/bash
set -e

echo "Starting Threads Auto Poster..."

# データベースマイグレーション
echo "Running database migrations..."
python -c "from threads.models.base import init_db; init_db()"

# Reflexアプリを起動
echo "Starting Reflex app..."
reflex run --env prod --backend-only --backend-port ${PORT:-8000}
