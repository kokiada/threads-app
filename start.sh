#!/bin/bash
set -e

# 古いプロセスをクリーンアップ
echo "Checking for existing processes..."
PORT=${PORT:-8000}
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Port $PORT is in use, killing existing process..."
    kill -9 $(lsof -t -i:$PORT) 2>/dev/null || true
    sleep 2
fi

echo "Initializing database..."
python -c "from threads.models import init_db; init_db(); print('Database initialized successfully')"

echo "Starting Reflex app on port $PORT..."
exec reflex run --env prod --loglevel info --backend-host 0.0.0.0 --backend-port $PORT
