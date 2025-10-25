import reflex as rx
from ..states.auth_state import AuthState

class AuthCallbackState(rx.State):
    def handle_callback(self):
        code = self.router.page.params.get("code", "")
        if code:
            return rx.redirect(f"/auth?code={code}")
        return rx.redirect("/auth")

def auth_callback_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.heading("認証処理中...", size="6"),
            rx.text("自動的にリダイレクトしています"),
            spacing="4",
            padding="4rem",
        ),
        height="100vh",
        on_mount=AuthCallbackState.handle_callback,
    )
