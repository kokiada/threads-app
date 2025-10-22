import reflex as rx
from ..components import sidebar
from ..states.post_state import PostState

def group_item(group: dict) -> rx.Component:
    return rx.button(
        group["name"],
        on_click=lambda: PostState.load_posts(group["id"]),
        variant="soft",
        width="100%",
    )

def post_card(post: dict) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(post["media_type"]),
                rx.button(
                    rx.icon("trash-2", size=16),
                    on_click=lambda: PostState.delete_post(post["id"]),
                    size="1",
                    color_scheme="red",
                    variant="soft",
                ),
                justify="between",
                width="100%",
            ),
            rx.text(post["text"], size="3"),
            spacing="3",
            align="start",
        ),
        width="100%",
    )

def posts_page() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            rx.hstack(
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.heading("グループ", size="5"),
                            rx.dialog.root(
                                rx.dialog.trigger(rx.button(rx.icon("plus", size=16), size="1")),
                                rx.dialog.content(
                                    rx.dialog.title("新規グループ"),
                                    rx.vstack(
                                        rx.input(
                                            placeholder="グループ名",
                                            value=PostState.form_group_name,
                                            on_change=PostState.set_form_group_name,
                                        ),
                                        rx.text_area(
                                            placeholder="説明",
                                            value=PostState.form_group_description,
                                            on_change=PostState.set_form_group_description,
                                        ),
                                        rx.hstack(
                                            rx.dialog.close(rx.button("キャンセル", variant="soft", color_scheme="gray")),
                                            rx.dialog.close(rx.button("作成", on_click=PostState.add_group)),
                                            spacing="3",
                                            justify="end",
                                            width="100%",
                                        ),
                                        spacing="4",
                                        width="100%",
                                    ),
                                ),
                            ),
                            justify="between",
                            width="100%",
                        ),
                        rx.foreach(PostState.groups, group_item),
                        spacing="3",
                        align="start",
                    ),
                    width="250px",
                    height="calc(100vh - 4rem)",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.heading("投稿一覧", size="6"),
                        rx.dialog.root(
                            rx.dialog.trigger(rx.button("投稿追加")),
                            rx.dialog.content(
                                rx.dialog.title("新規投稿"),
                                rx.vstack(
                                    rx.select(
                                        ["TEXT", "IMAGE", "VIDEO", "CAROUSEL"],
                                        value=PostState.form_media_type,
                                        on_change=PostState.set_form_media_type,
                                    ),
                                    rx.text_area(
                                        placeholder="投稿テキスト（最大500文字）",
                                        value=PostState.form_post_text,
                                        on_change=PostState.set_form_post_text,
                                        rows="5",
                                    ),
                                    rx.text_area(
                                        placeholder="メディアURL（1行に1つ）",
                                        value=PostState.form_media_urls,
                                        on_change=PostState.set_form_media_urls,
                                        rows="3",
                                    ),
                                    rx.hstack(
                                        rx.dialog.close(rx.button("キャンセル", variant="soft", color_scheme="gray")),
                                        rx.dialog.close(rx.button("追加", on_click=PostState.add_post)),
                                        spacing="3",
                                        justify="end",
                                        width="100%",
                                    ),
                                    spacing="4",
                                    width="100%",
                                ),
                            ),
                        ),
                        justify="between",
                        width="100%",
                    ),
                    rx.foreach(PostState.posts, post_card),
                    spacing="4",
                    padding="2rem",
                    align="start",
                    flex="1",
                ),
                spacing="4",
                align="start",
                height="100vh",
            ),
            margin_left="250px",
            on_mount=PostState.load_groups,
        ),
    )
