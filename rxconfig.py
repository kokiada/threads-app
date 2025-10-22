import reflex as rx

config = rx.Config(
    app_name="threads",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)