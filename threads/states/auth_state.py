import reflex as rx
import requests
import os
from datetime import datetime, timedelta

class AuthState(rx.State):
    auth_code: str = ""
    account_name: str = ""
    error_message: str = ""
    success_message: str = ""
    processing: bool = False
    callback_processed: bool = False
    
    @rx.var
    def auth_url(self) -> str:
        app_id = os.getenv("THREADS_APP_ID", "")
        base_url = os.getenv("BASE_URL", "http://localhost:3000")
        return f"https://threads.net/oauth/authorize?client_id={app_id}&redirect_uri={base_url}/auth/callback&scope=threads_basic,threads_content_publish&response_type=code"
    
    def on_load(self):
        pass
    
    def handle_callback(self):
        if self.callback_processed:
            return
        
        code = self.router.page.params.get("code", "")
        if code:
            self.callback_processed = True
            self._process_auth_code(code)
            return rx.redirect("/accounts")
    
    def set_auth_code(self, code: str):
        self.auth_code = code
    
    def set_account_name(self, name: str):
        self.account_name = name
    
    def _process_auth_code(self, code: str):
        from ..models.base import get_db
        from ..services.account_service import AccountService
        
        try:
            app_id = os.getenv("THREADS_APP_ID")
            app_secret = os.getenv("THREADS_APP_SECRET")
            base_url = os.getenv("BASE_URL", "http://localhost:3000")
            
            response = requests.post(
                "https://graph.threads.net/oauth/access_token",
                data={
                    "client_id": app_id,
                    "client_secret": app_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{base_url}/auth/callback",
                    "code": code
                }
            )
            response.raise_for_status()
            result = response.json()
            
            access_token = result.get("access_token")
            user_id = result.get("user_id")
            
            if access_token and user_id:
                db = next(get_db())
                try:
                    name = f"Account_{user_id[:8]}"
                    AccountService.create_account(
                        db=db,
                        name=name,
                        threads_user_id=user_id,
                        access_token=access_token,
                        token_expires_at=datetime.now() + timedelta(days=60)
                    )
                finally:
                    db.close()
        except Exception:
            pass
    
    def add_account(self):
        from ..models.base import get_db
        from ..services.account_service import AccountService
        
        if not self.auth_code:
            self.error_message = "認証コードを入力してください"
            return
        
        self.processing = True
        self.error_message = ""
        self.success_message = ""
        
        try:
            app_id = os.getenv("THREADS_APP_ID")
            app_secret = os.getenv("THREADS_APP_SECRET")
            base_url = os.getenv("BASE_URL", "http://localhost:3000")
            
            response = requests.post(
                "https://graph.threads.net/oauth/access_token",
                data={
                    "client_id": app_id,
                    "client_secret": app_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{base_url}/auth/callback",
                    "code": self.auth_code
                }
            )
            response.raise_for_status()
            result = response.json()
            
            access_token = result.get("access_token")
            user_id = result.get("user_id")
            
            if not access_token or not user_id:
                self.error_message = "トークン取得に失敗しました"
                self.processing = False
                return
            
            db = next(get_db())
            try:
                name = self.account_name or f"Account_{user_id[:8]}"
                AccountService.create_account(
                    db=db,
                    name=name,
                    threads_user_id=user_id,
                    access_token=access_token,
                    token_expires_at=datetime.now() + timedelta(days=60)
                )
                self.success_message = f"アカウント '{name}' を追加しました"
                self.auth_code = ""
                self.account_name = ""
            finally:
                db.close()
                
        except Exception as e:
            self.error_message = f"エラー: {str(e)}"
        finally:
            self.processing = False
