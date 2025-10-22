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
                            rx.link(
                                rx.button(
                                    "Threadsで認証する",
                                    size="3",
                                    color_scheme="blue",
                                ),
                                href=AuthState.auth_url,
                                is_external=True,
                            ),
                            rx.text("※ 新しいタブで開きます", size="2", color="gray"),
                        ),
                        spacing="4",
                    ),
                    width="100%",
                ),
                
                rx.card(
                    rx.vstack(
                        rx.heading("ステップ2: 認証コードを入力", size="6"),
                        rx.text("認証後、リダイレクトされたURLから 'code=' の後の文字列をコピーして貼り付けてください"),
                        rx.text("例: https://localhost:3000/auth/callback?code=AQBxxx...", size="2", color="gray"),
                        rx.input(
                            placeholder="認証コード（code=の後の文字列）",
                            value=AuthState.auth_code,
                            on_change=AuthState.set_auth_code,
                            width="100%",
                        ),
                        rx.button(
                            "アクセストークンを取得",
                            on_click=AuthState.exchange_token,
                        ),
                        spacing="4",
                    ),
                    width="100%",
                ),
                

                
                rx.cond(
                    AuthState.success_message != "",
                    rx.card(
                        rx.vstack(
                            rx.callout(
                                AuthState.success_message,
                                color_scheme="green",
                            ),
                            rx.heading("取得した情報", size="6"),
                            rx.vstack(
                                rx.hstack(
                                    rx.text("User ID:", weight="bold"),
                                    rx.text(AuthState.user_id),
                                ),
                                rx.hstack(
                                    rx.text("アクセストークン:", weight="bold"),
                                    rx.text(AuthState.access_token[:20] + "..."),
                                ),
                                rx.divider(),
                                rx.heading("アカウント登録", size="5"),
                                rx.text("アカウント名を入力して登録してください"),
                                rx.input(
                                    placeholder="アカウント名（例: マイアカウント）",
                                    value=AuthState.account_name,
                                    on_change=AuthState.set_account_name,
                                    width="100%",
                                ),
                                rx.button(
                                    "アカウントを登録",
                                    on_click=AuthState.register_account,
                                    size="3",
                                    color_scheme="green",
                                ),
                                spacing="3",
                            ),
                            spacing="4",
                        ),
                        width="100%",
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
            on_mount=AuthState.generate_auth_url,
        ),
    )
