import reflex as rx
import os

port = int(os.getenv("PORT", 8000))
base_url = os.getenv("BASE_URL", f"http://localhost:{port}")
is_prod = os.getenv("REFLEX_ENV") == "prod"

if is_prod:
    config = rx.Config(
        app_name="threads",
        backend_port=port,
        backend_host="0.0.0.0",
        api_url=base_url,
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
else:
    # ngrok使用時は同じURLを使用
    base_url_env = os.getenv("BASE_URL", "http://localhost:3000")
    config = rx.Config(
        app_name="threads",
        frontend_port=3000,
        backend_port=8000,
        backend_host="0.0.0.0",
        api_url=base_url_env,
        timeout=600,
        backend_transports=["polling"],
        plugins=[
            rx.plugins.SitemapPlugin(),
            rx.plugins.TailwindV4Plugin(),
        ]
    )
