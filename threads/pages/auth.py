import reflex as rx
from ..components import sidebar
from ..states.auth_state import AuthState

def auth_page() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            rx.vstack(
                rx.heading("アカウント追加", size="8"),
                
                rx.box(
                    rx.text(f"Debug: auth_code = {AuthState.auth_code}", size="1", color="gray"),
                    rx.text(f"Debug: account_name = {AuthState.account_name}", size="1", color="gray"),
                ),
                
                rx.card(
                    rx.vstack(
                        rx.heading("ステップ1: Threads認証", size="6"),
                        rx.text("以下のリンクから認証してください"),
                        rx.link(
                            rx.button("Threadsで認証", size="3", color_scheme="blue"),
                            href=AuthState.auth_url,
                            is_external=True,
                        ),
                        spacing="3",
                    ),
                    width="100%",
                ),
                
                rx.card(
                    rx.vstack(
                        rx.heading("ステップ2: 認証コード入力", size="6"),
                        rx.box(
                            rx.text("認証後、URLに含まれるcodeパラメータを以下に入力してください", size="2", color="gray"),
                            id="code_hint",
                        ),
                        rx.input(
                            placeholder="認証コード",
                            value=AuthState.auth_code,
                            on_change=AuthState.set_auth_code,
                            size="3",
                            id="code_input",
                        ),
                        rx.input(
                            placeholder="アカウント名（任意）",
                            value=AuthState.account_name,
                            on_change=AuthState.set_account_name,
                            size="3",
                        ),
                        rx.form(
                            rx.button(
                                "追加",
                                type="submit",
                                size="3",
                                color_scheme="green",
                                loading=AuthState.processing,
                            ),
                            on_submit=AuthState.add_account,
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
