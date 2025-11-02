#!/bin/bash
set -e

# 古いプロセスをクリーンアップ
echo "Checking for existing processes..."
FRONT_PORT=${PORT:-3000}
BACK_PORT=${BACKEND_PORT:-8000}

for p in $FRONT_PORT $BACK_PORT; do
    if lsof -Pi :$p -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "Port $p is in use, killing existing process..."
        kill -9 $(lsof -t -i:$p) 2>/dev/null || true
    fi
done
sleep 2

echo "Initializing database..."
python -c "from threads.models import init_db; init_db(); print('Database initialized successfully')"

echo "Starting Reflex app..."
echo "Frontend port: $FRONT_PORT"
echo "Backend port: $BACK_PORT"

# バックグラウンドでポート確認
(sleep 10 && echo "=== Port Check After 10s ===" && lsof -i :$FRONT_PORT && lsof -i :$BACK_PORT) &

exec reflex run --env prod --loglevel info --backend-host 0.0.0.0 --backend-port $BACK_PORT --frontend-port $FRONT_PORT
