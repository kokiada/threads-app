import reflex as rx
import requests
import os
from datetime import datetime, timedelta
from .base_state import BaseState

class AuthState(BaseState):
    auth_code: str = ""
    account_name: str = ""
    error_message: str = ""
    success_message: str = ""
    processing: bool = False
    callback_processed: bool = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import logging
        logger = logging.getLogger(__name__)
        logger.info("🔵 AuthState initialized")
    
    @rx.var
    def auth_url(self) -> str:
        app_id = os.getenv("THREADS_APP_ID", "")
        base_url = os.getenv("BASE_URL", "http://localhost:3000")
        return f"https://threads.net/oauth/authorize?client_id={app_id}&redirect_uri={base_url}/auth&scope=threads_basic,threads_content_publish&response_type=code"
    
    def on_load(self):
        # URLクエリパラメータからcodeを自動取得
        import logging
        logger = logging.getLogger(__name__)
        
        # クエリパラメータを取得
        code = self.router.page.params.get("code", "")
        logger.info(f"on_load: code from params = {code[:20] if code else 'None'}...")
        
        if code and not self.auth_code:
            # #_ を削除（Threads APIが末尾に追加する）
            code = code.replace("#_", "")
            self.auth_code = code
            logger.info(f"Auth code set: {code[:20]}...")
    
    def handle_callback(self):
        import logging
        logger = logging.getLogger(__name__)
        
        if self.callback_processed:
            logger.info("Callback already processed")
            return
        
        # URLパラメータからcodeを取得
        code = self.router.page.params.get("code", "")
        logger.info(f"Callback received with code: {code[:10] if code else 'None'}...")
        
        if code:
            self.callback_processed = True
            logger.info("Processing auth code...")
            self._process_auth_code(code)
            logger.info("Auth code processed successfully")
        else:
            logger.warning("No code parameter found in callback URL")
    
    def set_auth_code(self, code: str):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🔵 set_auth_code called: {code[:20] if code else 'empty'}...")
        self.auth_code = code
        logger.info(f"🔵 auth_code set successfully")
    
    def set_account_name(self, name: str):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🔵 set_account_name called: {name}")
        self.account_name = name
        logger.info(f"🔵 account_name set successfully")
    
    def _process_auth_code(self, code: str):
        import logging
        from ..models.base import get_db
        from ..services.account_service import AccountService
        
        logger = logging.getLogger(__name__)
        
        try:
            app_id = os.getenv("THREADS_APP_ID")
            app_secret = os.getenv("THREADS_APP_SECRET")
            base_url = os.getenv("BASE_URL", "http://localhost:3000")
            
            logger.info(f"Exchanging code for access token...")
            logger.info(f"Redirect URI: {base_url}/auth/callback")
            
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
            
            logger.info(f"Token exchange response: {result}")
            
            access_token = result.get("access_token")
            user_id = result.get("user_id")
            
            if access_token and user_id:
                db = next(get_db())
                try:
                    name = f"Account_{user_id[:8]}"
                    logger.info(f"Creating account: {name}")
                    AccountService.create_account(
                        db=db,
                        name=name,
                        threads_user_id=user_id,
                        access_token=access_token,
                        token_expires_at=datetime.now() + timedelta(days=60)
                    )
                    logger.info(f"Account created successfully: {name}")
                finally:
                    db.close()
            else:
                logger.error(f"Missing access_token or user_id in response")
        except Exception as e:
            logger.error(f"Error processing auth code: {str(e)}", exc_info=True)
    
    def add_account(self):
        import logging
        from ..models.base import get_db
        from ..services.account_service import AccountService
        
        logger = logging.getLogger(__name__)
        logger.info("="*80)
        logger.info("🟢 add_account METHOD CALLED")
        logger.info(f"🟢 Current auth_code: {self.auth_code[:20] if self.auth_code else 'EMPTY'}...")
        logger.info(f"🟢 Current account_name: {self.account_name}")
        logger.info(f"🟢 Current processing: {self.processing}")
        logger.info("="*80)
        
        if not self.auth_code:
            self.error_message = "認証コードを入力してください"
            logger.warning("No auth code provided")
            return
        
        self.processing = True
        self.error_message = ""
        self.success_message = ""
        logger.info("Starting token exchange...")
        
        try:
            app_id = os.getenv("THREADS_APP_ID")
            app_secret = os.getenv("THREADS_APP_SECRET")
            base_url = os.getenv("BASE_URL", "http://localhost:3000")
            
            logger.info(f"Requesting token with redirect_uri: {base_url}/auth")
            response = requests.post(
                "https://graph.threads.net/oauth/access_token",
                data={
                    "client_id": app_id,
                    "client_secret": app_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{base_url}/auth",
                    "code": self.auth_code
                }
            )
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response body: {response.text}")
            response.raise_for_status()
            result = response.json()
            logger.info(f"Token exchange successful: {result}")
            
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
                logger.info(f"Account added successfully: {name}")
                self.auth_code = ""
                self.account_name = ""
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in add_account: {str(e)}", exc_info=True)
            self.error_message = f"エラー: {str(e)}"
        finally:
            self.processing = False
            logger.info("add_account completed")
