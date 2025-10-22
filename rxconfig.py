import reflex as rx
import os

config = rx.Config(
    app_name="threads",
    frontend_port=int(os.getenv("PORT", 3000)),
    backend_port=8000,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)