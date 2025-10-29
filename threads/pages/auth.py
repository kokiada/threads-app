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
                        ),
                        spacing="4",
                    ),
                    width="100%",
                ),
                
                rx.card(
                    rx.vstack(
                        rx.heading("ステップ2: アカウント名を入力", size="6"),
                        rx.text("認証後、アカウント名を入力してください（任意）"),
                        rx.script(
                            """
                            setTimeout(function() {
                                const params = new URLSearchParams(window.location.search);
                                const code = params.get('code');
                                if (code) {
                                    const input = document.querySelector('input[placeholder*="認証コード"]');
                                    if (input) {
                                        input.value = code;
                                        input.dispatchEvent(new Event('change', { bubbles: true }));
                                    }
                                }
                            }, 300);
                            """
                        ),
                        rx.input(
                            placeholder="認証コード（自動入力）",
                            value=AuthState.auth_code,
                            on_change=AuthState.set_auth_code,
                            size="3",
                            read_only=True,
                        ),
                        rx.input(
                            placeholder="Threads User IDを入力",
                            value=AuthState.user_id,
                            on_change=AuthState.set_user_id,
                            size="3",
                        ),
                        rx.input(
                            placeholder="アカウント名（例: メインアカウント）",
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
        ),
    )
