import reflex as rx
from ..components import sidebar
from ..states.auth_state import AuthState

def auth_page() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            rx.vstack(
                rx.heading("Threads API 認証", size="8"),
                
                rx.card(
                    rx.vstack(
                        rx.heading("ステップ1: 認証URLを開く", size="6"),
                        rx.text("認証を開始するには、以下のリンクをクリックしてください"),
                        rx.vstack(
                            rx.text("認証リンク:", weight="bold"),
                            rx.cond(
                                AuthState.computed_auth_url != "",
                                rx.link(
                                    rx.button(
                                        "Threadsで認証する",
                                        size="3",
                                        color_scheme="blue",
                                    ),
                                    href=AuthState.computed_auth_url,
                                    is_external=True,
                                ),
                                rx.text("URLを生成中...", color="gray"),
                            ),
                            rx.text("※ 新しいタブで開きます", size="2", color="gray"),
                            rx.text(AuthState.computed_auth_url, size="1", color="gray"),
                        ),
                        spacing="4",
                    ),
                    width="100%",
                ),
                
                rx.cond(
                    AuthState.auth_code != "",
                    rx.card(
                        rx.vstack(
                            rx.heading("ステップ2: User IDとアカウント名を入力", size="6"),
                            rx.text("認証コードを取得しました！", color="green"),
                            rx.input(
                                placeholder="Threads User IDを入力",
                                value=AuthState.user_id,
                                on_change=AuthState.set_user_id,
                                size="3",
                            ),
                            rx.input(
                                placeholder="アカウント名を入力",
                                value=AuthState.account_name,
                                on_change=AuthState.set_account_name,
                                size="3",
                            ),
                            rx.button(
                                "アカウントを追加",
                                on_click=AuthState.manual_register_account,
                                size="3",
                                color_scheme="green",
                            ),
                            spacing="4",
                        ),
                        width="100%",
                    ),
                ),
                
                rx.cond(
                    AuthState.processing,
                    rx.card(
                        rx.vstack(
                            rx.spinner(size="3"),
                            rx.text("認証処理中...", size="4", weight="bold"),
                            spacing="3",
                            align="center",
                            padding="2rem",
                        ),
                        width="100%",
                    ),
                    rx.cond(
                        AuthState.success_message != "",
                        rx.callout(
                            AuthState.success_message,
                            color_scheme="green",
                            size="3",
                        ),
                    ),
                ),
                
                rx.cond(
                    AuthState.error_message != "",
                    rx.callout(
                        AuthState.error_message,
                        color_scheme="red",
                    ),
                ),
                

                

                
                spacing="6",
                padding="2rem",
                align="start",
            ),
            margin_left="250px",
            width="100%",
            on_mount=AuthState.extract_code_from_url,
        ),
    )
