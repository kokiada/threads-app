import reflex as rx
import logging
import sys
import signal
import atexit
from .pages import (
    dashboard_page,
    accounts_page,
    posts_page,
    schedules_page,
    manual_post_page,
    metrics_page,
    auth_page,
    auth_callback_page,
)
from .scheduler import start_scheduler

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def cleanup():
    logger.info("Cleaning up resources...")

def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
atexit.register(cleanup)

app = rx.App()
app.add_page(dashboard_page, route="/", title="ダッシュボード")
app.add_page(accounts_page, route="/accounts", title="アカウント管理")
app.add_page(posts_page, route="/posts", title="投稿管理")
app.add_page(schedules_page, route="/schedules", title="スケジュール設定")
app.add_page(manual_post_page, route="/manual-post", title="手動投稿")
app.add_page(metrics_page, route="/metrics", title="メトリクス分析")
app.add_page(auth_page, route="/auth", title="アカウント追加")
app.add_page(auth_callback_page, route="/auth/callback", title="認証処理中")

# 静的ファイル配信
from fastapi.staticfiles import StaticFiles
import os
uploaded_files_dir = "uploaded_files"
os.makedirs(uploaded_files_dir, exist_ok=True)
app.api.mount("/uploaded_files", StaticFiles(directory=uploaded_files_dir), name="uploaded_files")

# スケジューラー起動（デバッグ時は無効化）
# start_scheduler()
