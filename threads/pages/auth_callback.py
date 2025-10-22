import reflex as rx
from ..states.auth_state import AuthState

def auth_callback_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.heading("認証処理中...", size="6"),
            rx.text("自動的にトークンを取得しています"),
            spacing="4",
            padding="4rem",
        ),
        height="100vh",
        on_mount=AuthState.handle_callback,
    )
