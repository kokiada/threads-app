import reflex as rx
from ..components import sidebar
from ..states.manual_post_state import ManualPostState

def manual_post_page() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            rx.vstack(
                rx.heading("手動投稿", size="8"),
                
                rx.card(
                    rx.vstack(
                        rx.heading("アカウント選択", size="6"),
                        rx.foreach(
                            ManualPostState.accounts,
                            lambda a: rx.checkbox(
                                a["name"],
                                on_change=lambda: ManualPostState.toggle_account(a["id"]),
                            ),
                        ),
                        spacing="2",
                    ),
                    width="100%",
                ),
                
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("直接入力", value="direct"),
                        rx.tabs.trigger("テンプレートから", value="template"),
                    ),
                    rx.tabs.content(
                        rx.card(
                            rx.vstack(
                                rx.select(
                                    ["TEXT", "IMAGE", "VIDEO", "CAROUSEL"],
                                    value=ManualPostState.media_type,
                                    on_change=ManualPostState.set_media_type,
                                ),
                                rx.text_area(
                                    placeholder="投稿内容（500文字以内）",
                                    value=ManualPostState.post_text,
                                    on_change=ManualPostState.set_post_text,
                                    rows="5",
                                ),
                                rx.cond(
                                    ManualPostState.media_type != "TEXT",
                                    rx.input(
                                        placeholder="メディアURL（複数の場合はカンマ区切り）",
                                        value=ManualPostState.media_urls,
                                        on_change=ManualPostState.set_media_urls,
                                    ),
                                ),
                                rx.button(
                                    "投稿実行",
                                    on_click=ManualPostState.post_manual,
                                    loading=ManualPostState.posting,
                                ),
                                spacing="4",
                            ),
                            width="100%",
                        ),
                        value="direct",
                    ),
                    rx.tabs.content(
                        rx.card(
                            rx.vstack(
                                rx.select(
                                    ManualPostState.groups.map(lambda g: g["name"]),
                                    placeholder="グループを選択",
                                    on_change=ManualPostState.set_selected_group_id,
                                ),
                                rx.select(
                                    ManualPostState.posts.map(lambda p: p["text"]),
                                    placeholder="投稿を選択",
                                    on_change=ManualPostState.set_selected_post_id,
                                ),
                                rx.button(
                                    "投稿実行",
                                    on_click=ManualPostState.post_from_template,
                                    loading=ManualPostState.posting,
                                ),
                                spacing="4",
                            ),
                            width="100%",
                        ),
                        value="template",
                    ),
                    default_value="direct",
                ),
                
                rx.cond(
                    ManualPostState.result_message != "",
                    rx.callout(
                        ManualPostState.result_message,
                        color_scheme="green",
                    ),
                ),
                
                spacing="6",
                padding="2rem",
                align="start",
            ),
            margin_left="250px",
            on_mount=[
                ManualPostState.load_accounts,
                ManualPostState.load_groups,
            ],
        ),
    )
