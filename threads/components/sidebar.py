import reflex as rx

def sidebar_item(text: str, icon: str, href: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=20),
            rx.text(text, size="3"),
            padding="0.75rem",
            border_radius="0.5rem",
            _hover={"bg": rx.color("accent", 3)},
            width="100%",
        ),
        href=href,
        text_decoration="none",
        color="inherit",
    )

def sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("Threads Auto Poster", size="6", margin_bottom="2rem"),
            sidebar_item("ダッシュボード", "layout-dashboard", "/"),
            sidebar_item("アカウント管理", "users", "/accounts"),
            sidebar_item("投稿管理", "file-text", "/posts"),
            sidebar_item("スケジュール", "calendar", "/schedules"),
            sidebar_item("手動投稿", "send", "/manual-post"),
            sidebar_item("メトリクス", "bar-chart", "/metrics"),
            rx.divider(),
            sidebar_item("API認証", "key", "/auth"),
            spacing="2",
            align="stretch",
        ),
        width="250px",
        padding="2rem",
        bg=rx.color("gray", 2),
        height="100vh",
        position="fixed",
    )
