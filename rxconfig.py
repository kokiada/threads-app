import reflex as rx
import os

port = int(os.getenv("PORT", 3000))
backend_port = int(os.getenv("BACKEND_PORT", 8000))
base_url = os.getenv("BASE_URL", "http://localhost:3000")
is_prod = os.getenv("REFLEX_ENV") == "prod"

# api_urlは常にバックエンドを指す
api_url = f"http://localhost:{backend_port}"

config = rx.Config(
    app_name="threads",
    frontend_port=port,
    backend_port=backend_port,
    backend_host="0.0.0.0",
    api_url=api_url,
    timeout=600,
    backend_transports=["polling", "websocket"],
    gunicorn_worker_class="uvicorn.workers.UvicornWorker",
    gunicorn_workers=1,
    gunicorn_timeout=600,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)
