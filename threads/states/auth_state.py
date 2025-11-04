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
            user_id = str(result.get("user_id"))
            
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
            
            # ステップ1: 短期トークン取得
            logger.info("Step 1: 短期トークン取得")
            short_token_response = requests.post(
                "https://graph.threads.net/oauth/access_token",
                data={
                    "client_id": app_id,
                    "client_secret": app_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{base_url}/auth",
                    "code": self.auth_code
                }
            )
            logger.info(f"Response status: {short_token_response.status_code}")
            logger.info(f"Response body: {short_token_response.text}")
            short_token_response.raise_for_status()
            short_result = short_token_response.json()
            
            short_token = short_result.get("access_token")
            user_id = str(short_result.get("user_id"))
            
            if not short_token or not user_id:
                self.error_message = "短期トークン取得に失敗しました"
                self.processing = False
                return
            
            logger.info(f"短期トークン取得成功: user_id={user_id}")
            
            # ステップ2: 長期トークン取得
            logger.info("Step 2: 長期トークン取得")
            long_token_response = requests.get(
                "https://graph.threads.net/access_token",
                params={
                    "grant_type": "th_exchange_token",
                    "client_secret": app_secret,
                    "access_token": short_token
                }
            )
            long_token_response.raise_for_status()
            long_result = long_token_response.json()
            
            long_token = long_result.get("access_token")
            expires_in = long_result.get("expires_in", 5184000)  # デフォルト60日
            
            if not long_token:
                self.error_message = "長期トークン取得に失敗しました"
                self.processing = False
                return
            
            logger.info(f"長期トークン取得成功: expires_in={expires_in}秒")
            
            # ステップ3: アカウント追加
            logger.info("Step 3: アカウント追加")
            db = next(get_db())
            try:
                name = self.account_name or f"Account_{user_id[:8]}"
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                AccountService.create_account(
                    db=db,
                    name=name,
                    threads_user_id=user_id,
                    access_token=long_token,
                    token_expires_at=expires_at
                )
                self.success_message = f"アカウント '{name}' を追加しました"
                logger.info(f"アカウント追加成功: {name}")
                self.auth_code = ""
                self.account_name = ""
            finally:
                db.close()
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTPエラー: {str(e)}", exc_info=True)
            error_detail = e.response.text if hasattr(e, 'response') else str(e)
            self.error_message = f"認証エラー: {error_detail}"
        except Exception as e:
            logger.error(f"エラー: {str(e)}", exc_info=True)
            self.error_message = f"エラー: {str(e)}"
        finally:
            self.processing = False
