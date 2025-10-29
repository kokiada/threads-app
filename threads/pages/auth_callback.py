import reflex as rx

def auth_callback_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.heading("認証処理中...", size="6"),
            rx.text("自動的にリダイレクトしています"),
            rx.script(
                """
                window.addEventListener('load', function() {
                    const params = new URLSearchParams(window.location.search);
                    const code = params.get('code');
                    const targetUrl = code ? '/auth?code=' + encodeURIComponent(code) : '/auth';
                    window.location.replace(targetUrl);
                });
                """
            ),
            spacing="4",
            padding="4rem",
        ),
        height="100vh",
    )
