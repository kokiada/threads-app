import reflex as rx
from ..states.auth_state import AuthState

def auth_callback_page() -> rx.Component:
    return rx.fragment(
        rx.script(
            """
            setTimeout(function() {
                const urlParams = new URLSearchParams(window.location.search);
                const code = urlParams.get('code');
                console.log('Callback - code:', code);
                if (code) {
                    window.location.replace('/auth?code=' + encodeURIComponent(code));
                } else {
                    window.location.replace('/auth');
                }
            }, 100);
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
