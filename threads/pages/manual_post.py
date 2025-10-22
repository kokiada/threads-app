import reflex as rx
from ..components import sidebar

def manual_post_page() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            rx.vstack(
                rx.heading("手動投稿", size="8"),
                rx.card(
                    rx.text("手動投稿機能は実装中です", color=rx.color("gray", 11)),
                    width="100%",
                ),
                spacing="6",
                padding="2rem",
                align="start",
            ),
            margin_left="250px",
        ),
    )
