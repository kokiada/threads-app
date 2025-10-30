import reflex as rx
from ..components import sidebar
from ..states.auth_state import AuthState

def auth_page() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            rx.vstack(
                rx.heading("アカウント追加", size="8"),
                
                rx.card(
                    rx.vstack(
                        rx.heading("ステップ1: Threads認証", size="6"),
                        rx.text("以下のリンクから認証してください"),
                        rx.link(
                            rx.button("Threadsで認証", size="3", color_scheme="blue"),
                            href=f"https://threads.net/oauth/authorize?client_id={rx.Var.create(lambda: __import__('os').getenv('THREADS_APP_ID'))}&redirect_uri={rx.Var.create(lambda: __import__('os').getenv('BASE_URL', 'http://localhost:3000'))}/auth/callback&scope=threads_basic,threads_content_publish&response_type=code",
                            is_external=True,
                        ),
                        spacing="3",
                    ),
                    width="100%",
                ),
                
                rx.card(
                    rx.vstack(
                        rx.heading("ステップ2: 認証コード入力", size="6"),
                        rx.input(
                            placeholder="認証コード",
                            value=AuthState.auth_code,
                            on_change=AuthState.set_auth_code,
                            size="3",
                        ),
                        rx.input(
                            placeholder="アカウント名（任意）",
                            value=AuthState.account_name,
                            on_change=AuthState.set_account_name,
                            size="3",
                        ),
                        rx.button(
                            "追加",
                            on_click=AuthState.add_account,
                            size="3",
                            color_scheme="green",
                            loading=AuthState.processing,
                        ),
                        spacing="3",
                    ),
                    width="100%",
                ),
                
                rx.cond(
                    AuthState.error_message != "",
                    rx.callout(AuthState.error_message, color_scheme="red"),
                ),
                
                rx.cond(
                    AuthState.success_message != "",
                    rx.callout(AuthState.success_message, color_scheme="green"),
                ),
                
                spacing="6",
                padding="2rem",
                on_mount=AuthState.on_load,
            ),
            margin_left="250px",
        ),
    )
