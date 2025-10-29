import reflex as rx

def auth_callback_page() -> rx.Component:
    return rx.fragment(
        rx.html(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Redirecting...</title>
                <script>
                    const params = new URLSearchParams(window.location.search);
                    const code = params.get('code');
                    const targetUrl = code ? '/auth?code=' + encodeURIComponent(code) : '/auth';
                    window.location.replace(targetUrl);
                </script>
            </head>
            <body>
                <div style="display: flex; justify-content: center; align-items: center; height: 100vh; font-family: sans-serif;">
                    <div style="text-align: center;">
                        <div style="margin-bottom: 20px;">認証処理中...</div>
                        <div>自動的にリダイレクトしています</div>
                    </div>
                </div>
            </body>
            </html>
            """
        )
    )
