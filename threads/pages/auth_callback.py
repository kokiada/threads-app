import reflex as rx
from ..states.auth_state import AuthState

def auth_callback_page() -> rx.Component:
    return rx.fragment(
        rx.script(
            """
            const urlParams = new URLSearchParams(window.location.search);
            const code = urlParams.get('code');
            if (code) {
                window.location.href = '/auth?code=' + code;
            }
            """
        ),
        rx.center(
            rx.vstack(
                rx.spinner(size="3"),
                rx.heading("認証処理中...", size="6"),
                rx.text("自動的にリダイレクトしています"),
                spacing="4",
                padding="4rem",
            ),
            height="100vh",
        ),
    )
