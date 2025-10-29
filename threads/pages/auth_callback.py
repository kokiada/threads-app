import reflex as rx

def auth_callback_page() -> rx.Component:
    return rx.fragment(
        rx.script(
            """
            (function() {
                // WebSocket接続前に即座にリダイレクト
                const params = new URLSearchParams(window.location.search);
                const code = params.get('code');
                const targetUrl = code ? `/auth?code=${encodeURIComponent(code)}` : '/auth';
                
                // エラーログを抑制
                const originalError = console.error;
                console.error = function(...args) {
                    if (args[0] && args[0].toString().includes('WebSocket')) {
                        return; // WebSocketエラーを無視
                    }
                    originalError.apply(console, args);
                };
                
                window.location.replace(targetUrl);
            })();
            """
        ),
        rx.center(
            rx.vstack(
                rx.spinner(size="3"),
                rx.heading("認証処理中...", size="6"),
                rx.text("自動的にリダイレクトしています"),
                spacing="4",
                padding="4rem",
            ),
            height="100vh",
        ),
    )
