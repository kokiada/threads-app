import reflex as rx
from ..components import sidebar
from ..states.manual_post_state import ManualPostState

def manual_post_page() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            rx.vstack(
                rx.heading("手動投稿", size="9", margin_bottom="2rem"),
                
                rx.grid(
                    rx.box(
                        rx.card(
                            rx.vstack(
                                rx.heading("アカウント選択", size="6", margin_bottom="1rem"),
                                rx.scroll_area(
                                    rx.vstack(
                                        rx.foreach(
                                            ManualPostState.accounts,
                                            lambda a: rx.hstack(
                                                rx.checkbox(
                                                    on_change=lambda checked, aid=a["id"]: ManualPostState.set_account_selection(aid, checked),
                                                    size="3",
                                                ),
                                                rx.text(a["name"], size="3"),
                                                spacing="2",
                                            ),
                                        ),
                                        spacing="3",
                                        width="100%",
                                    ),
                                    height="400px",
                                ),
                                spacing="4",
                                width="100%",
                            ),
                            height="500px",
                        ),
                    ),
                    
                    rx.box(
                        rx.tabs.root(
                            rx.tabs.list(
                                rx.tabs.trigger("直接入力", value="direct", size="3"),
                                rx.tabs.trigger("テンプレートから", value="template", size="3"),
                            ),
                            rx.tabs.content(
                                rx.card(
                                    rx.scroll_area(
                                        rx.vstack(
                                            rx.text("メディアタイプ", weight="bold", size="4"),
                                            rx.select(
                                                ["TEXT", "IMAGE", "VIDEO", "CAROUSEL"],
                                                value=ManualPostState.media_type,
                                                on_change=ManualPostState.set_media_type,
                                                size="3",
                                            ),
                                            rx.text("投稿内容", weight="bold", size="4", margin_top="1rem"),
                                            rx.text_area(
                                                placeholder="投稿内容を入力（500文字以内）",
                                                value=ManualPostState.post_text,
                                                on_change=ManualPostState.set_post_text,
                                                rows="8",
                                                width="100%",
                                                size="3",
                                            ),
                                            rx.cond(
                                                ManualPostState.media_type != "TEXT",
                                                rx.vstack(
                                                    rx.text("メディア", weight="bold", size="4"),
                                                    rx.upload(
                                                        rx.button(
                                                            "ファイルを選択",
                                                            size="3",
                                                        ),
                                                        id="upload",
                                                        multiple=True,
                                                        accept={
                                                            "image/*": [".jpg", ".jpeg", ".png", ".gif"],
                                                            "video/*": [".mp4", ".mov"],
                                                        },
                                                    ),
                                                    rx.button(
                                                        "アップロード",
                                                        on_click=ManualPostState.handle_upload(rx.upload_files(upload_id="upload")),
                                                        loading=ManualPostState.uploading,
                                                        size="3",
                                                    ),
                                                    rx.text("またはURLを直接入力", size="2", color="gray"),
                                                    rx.input(
                                                        placeholder="メディアURL（複数の場合はカンマ区切り）",
                                                        value=ManualPostState.media_urls,
                                                        on_change=ManualPostState.set_media_urls,
                                                        width="100%",
                                                        size="3",
                                                    ),
                                                    spacing="2",
                                                    width="100%",
                                                ),
                                            ),
                                            rx.cond(
                                                ManualPostState.posting,
                                                rx.vstack(
                                                    rx.spinner(size="3"),
                                                    rx.text("投稿中...", size="4", weight="bold"),
                                                    spacing="3",
                                                    align="center",
                                                    width="100%",
                                                    padding="2rem",
                                                ),
                                                rx.button(
                                                    "投稿実行",
                                                    on_click=ManualPostState.post_manual,
                                                    size="4",
                                                    width="100%",
                                                    margin_top="2rem",
                                                ),
                                            ),
                                            spacing="4",
                                            width="100%",
                                            padding="1rem",
                                        ),
                                        height="450px",
                                    ),
                                    height="500px",
                                ),
                                value="direct",
                            ),
                            rx.tabs.content(
                                rx.card(
                                    rx.scroll_area(
                                        rx.vstack(
                                            rx.text("グループ選択", weight="bold", size="4"),
                                            rx.select.root(
                                                rx.select.trigger(placeholder="グループを選択", size="3"),
                                                rx.select.content(
                                                    rx.foreach(
                                                        ManualPostState.groups,
                                                        lambda g: rx.select.item(g["name"], value=g["id"]),
                                                    ),
                                                ),
                                                on_change=ManualPostState.set_selected_group_id,
                                                width="100%",
                                            ),
                                            rx.text("投稿テンプレート選択", weight="bold", size="4", margin_top="1rem"),
                                            rx.select.root(
                                                rx.select.trigger(placeholder="投稿を選択", size="3"),
                                                rx.select.content(
                                                    rx.foreach(
                                                        ManualPostState.posts,
                                                        lambda p: rx.select.item(p["text"], value=p["id"]),
                                                    ),
                                                ),
                                                on_change=ManualPostState.set_selected_post_id,
                                                width="100%",
                                            ),
                                            rx.cond(
                                                ManualPostState.posting,
                                                rx.vstack(
                                                    rx.spinner(size="3"),
                                                    rx.text("投稿中...", size="4", weight="bold"),
                                                    spacing="3",
                                                    align="center",
                                                    width="100%",
                                                    padding="2rem",
                                                ),
                                                rx.button(
                                                    "投稿実行",
                                                    on_click=ManualPostState.post_from_template,
                                                    size="4",
                                                    width="100%",
                                                    margin_top="2rem",
                                                ),
                                            ),
                                            spacing="4",
                                            width="100%",
                                            padding="1rem",
                                        ),
                                        height="450px",
                                    ),
                                    height="500px",
                                ),
                                value="template",
                            ),
                            default_value="direct",
                            width="100%",
                        ),
                    ),
                    columns="2",
                    spacing="6",
                    width="100%",
                ),
                
                rx.cond(
                    ManualPostState.result_message != "",
                    rx.callout(
                        ManualPostState.result_message,
                        color_scheme="green",
                        size="3",
                        width="100%",
                    ),
                ),
                
                spacing="6",
                padding="2rem",
                width="100%",
            ),
            margin_left="250px",
            padding="2rem",
            width="calc(100% - 250px)",
            min_height="100vh",
            on_mount=[
                ManualPostState.load_accounts,
                ManualPostState.load_groups,
            ],
        ),
    )
