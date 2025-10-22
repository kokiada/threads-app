#!/bin/bash
set -e

# データベース初期化
python scripts/init_db.py

# Reflexアプリ起動
exec reflex run --env prod
