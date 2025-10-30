import reflex as rx
import os

port = int(os.getenv("PORT", 3000))
base_url = os.getenv("BASE_URL", f"http://localhost:{port}")
is_prod = os.getenv("REFLEX_ENV") == "prod"

config = rx.Config(
    app_name="threads",
    frontend_port=port,
    backend_port=port,
    backend_host="0.0.0.0",
    api_url=base_url,
    timeout=120,
    backend_transports=["websocket", "polling"],
    gunicorn_worker_class="uvicorn.workers.UvicornWorker",
    gunicorn_workers=1,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)