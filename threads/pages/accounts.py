import reflex as rx
from ..components import sidebar
from ..states.account_state import AccountState

def account_row(account: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(account["name"]),
        rx.table.cell(account["threads_user_id"]),
        rx.table.cell(
            rx.badge(account["status"], color_scheme="green" if account["status"] == "active" else "gray")
        ),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("power", size=16),
                    on_click=lambda: AccountState.toggle_status(account["id"]),
                    size="1",
                    variant="soft",
                ),
                rx.button(
                    rx.icon("trash-2", size=16),
                    on_click=lambda: AccountState.delete_account(account["id"]),
                    size="1",
                    color_scheme="red",
                    variant="soft",
                ),
                spacing="2",
            )
        ),
    )

def add_account_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button("アカウント追加", on_click=AccountState.open_add_modal)
        ),
        rx.dialog.content(
            rx.dialog.title("新規アカウント追加"),
            rx.vstack(
                rx.input(
                    placeholder="アカウント名",
                    value=AccountState.form_name,
                    on_change=AccountState.set_form_name,
                ),
                rx.input(
                    placeholder="Threads User ID",
                    value=AccountState.form_threads_user_id,
                    on_change=AccountState.set_form_threads_user_id,
                ),
                rx.input(
                    placeholder="アクセストークン",
                    type="password",
                    value=AccountState.form_access_token,
                    on_change=AccountState.set_form_access_token,
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("キャンセル", variant="soft", color_scheme="gray")
                    ),
                    rx.dialog.close(
                        rx.button("追加", on_click=AccountState.add_account)
                    ),
                    spacing="3",
                    justify="end",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            open=AccountState.show_add_modal,
        ),
    )

def accounts_page() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.heading("アカウント管理", size="8"),
                    add_account_modal(),
                    justify="between",
                    width="100%",
                ),
                rx.card(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("名前"),
                                rx.table.column_header_cell("User ID"),
                                rx.table.column_header_cell("ステータス"),
                                rx.table.column_header_cell("操作"),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(AccountState.accounts, account_row)
                        ),
                    ),
                    width="100%",
                ),
                spacing="6",
                padding="2rem",
                align="start",
            ),
            margin_left="250px",
            on_mount=AccountState.load_accounts,
        ),
    )
