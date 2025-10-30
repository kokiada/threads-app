import reflex as rx

def auth_callback_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.heading("認証処理中...", size="6"),
            rx.script(
                """
                const params = new URLSearchParams(window.location.search);
                const code = params.get('code');
                if (code) {
                    sessionStorage.setItem('threads_auth_code', code);
                    window.location.href = '/auth';
                } else {
                    window.location.href = '/auth';
                }
                """
            ),
            spacing="4",
            padding="4rem",
        ),
        height="100vh",
    )
