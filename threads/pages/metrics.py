import reflex as rx
from ..components import sidebar
from ..states.metrics_state import MetricsState

def metrics_page() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            rx.vstack(
                rx.heading("メトリクス分析", size="8"),
                
                rx.card(
                    rx.vstack(
                        rx.heading("成長ランキング TOP 10", size="6"),
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("アカウント"),
                                    rx.table.column_header_cell("成長率"),
                                    rx.table.column_header_cell("フォロワー数"),
                                ),
                            ),
                            rx.table.body(
                                rx.foreach(
                                    MetricsState.top_accounts,
                                    lambda a: rx.table.row(
                                        rx.table.cell(a["account_name"]),
                                        rx.table.cell(a["growth_rate"]),
                                        rx.table.cell(a["followers"]),
                                    ),
                                ),
                            ),
                        ),
                        spacing="4",
                    ),
                    width="100%",
                ),
                
                rx.card(
                    rx.vstack(
                        rx.heading("アカウント別メトリクス", size="6"),
                        rx.select(
                            [a["name"] for a in MetricsState.accounts],
                            placeholder="アカウントを選択",
                            on_change=MetricsState.set_selected_account_id,
                        ),
                        rx.button(
                            "メトリクス取得",
                            on_click=MetricsState.fetch_metrics,
                            loading=MetricsState.loading,
                        ),
                        rx.cond(
                            MetricsState.account_metrics != {},
                            rx.grid(
                                rx.card(
                                    rx.vstack(
                                        rx.text("視聴数", size="2", color=rx.color("gray", 11)),
                                        rx.text(MetricsState.account_metrics["views"], size="6", weight="bold"),
                                    ),
                                ),
                                rx.card(
                                    rx.vstack(
                                        rx.text("いいね", size="2", color=rx.color("gray", 11)),
                                        rx.text(MetricsState.account_metrics["likes"], size="6", weight="bold"),
                                    ),
                                ),
                                rx.card(
                                    rx.vstack(
                                        rx.text("返信", size="2", color=rx.color("gray", 11)),
                                        rx.text(MetricsState.account_metrics["replies"], size="6", weight="bold"),
                                    ),
                                ),
                                rx.card(
                                    rx.vstack(
                                        rx.text("リポスト", size="2", color=rx.color("gray", 11)),
                                        rx.text(MetricsState.account_metrics["reposts"], size="6", weight="bold"),
                                    ),
                                ),
                                rx.card(
                                    rx.vstack(
                                        rx.text("フォロワー", size="2", color=rx.color("gray", 11)),
                                        rx.text(MetricsState.account_metrics["followers_count"], size="6", weight="bold"),
                                    ),
                                ),
                                columns="5",
                                spacing="4",
                            ),
                        ),
                        spacing="4",
                    ),
                    width="100%",
                ),
                
                spacing="6",
                padding="2rem",
                align="start",
            ),
            margin_left="250px",
            on_mount=[
                MetricsState.load_accounts,
                MetricsState.load_top_accounts,
            ],
        ),
    )
