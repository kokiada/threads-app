import reflex as rx
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

app = rx.App()
app.add_page(dashboard_page, route="/")
app.add_page(accounts_page, route="/accounts")
app.add_page(posts_page, route="/posts")
app.add_page(schedules_page, route="/schedules")
app.add_page(manual_post_page, route="/manual-post")
app.add_page(metrics_page, route="/metrics")
app.add_page(auth_page, route="/auth")
app.add_page(auth_callback_page, route="/auth/callback")

# スケジューラー起動
start_scheduler()
