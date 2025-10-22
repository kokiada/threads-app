import reflex as rx
from ..components import sidebar

def dashboard_page() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            rx.vstack(
                rx.heading("ダッシュボード", size="8"),
                rx.hstack(
                    rx.card(
                        rx.vstack(
                            rx.text("総アカウント数", size="2", color=rx.color("gray", 11)),
                            rx.heading("0", size="7"),
                            spacing="2",
                        ),
                        width="250px",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.text("今日の投稿数", size="2", color=rx.color("gray", 11)),
                            rx.heading("0", size="7"),
                            spacing="2",
                        ),
                        width="250px",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.text("アクティブスケジュール", size="2", color=rx.color("gray", 11)),
                            rx.heading("0", size="7"),
                            spacing="2",
                        ),
                        width="250px",
                    ),
                    spacing="4",
                ),
                rx.card(
                    rx.vstack(
                        rx.heading("成長アカウントランキング", size="5"),
                        rx.text("データがありません", color=rx.color("gray", 11)),
                        spacing="3",
                        align="start",
                    ),
                    width="100%",
                ),
                spacing="6",
                padding="2rem",
                align="start",
            ),
            margin_left="250px",
        ),
    )
