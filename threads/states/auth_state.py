import reflex as rx
import requests
import os
from typing import Optional

class AuthState(rx.State):
    auth_url: str = ""
    auth_code: str = ""
    access_token: str = ""
    user_id: str = ""
    error_message: str = ""
    success_message: str = ""
    processing: bool = False
    debug_log: str = "Initialized"
    
    def on_load(self):
        """ページロード時にURLパラメータからcodeを取得"""
        import logging
        logger = logging.getLogger(__name__)
        
        code = self.router.page.params.get("code", "")
        print(f"DEBUG: on_load called, code from URL: {code[:20] if code else 'None'}")
        logger.info(f"DEBUG: on_load called, code from URL: {code[:20] if code else 'None'}")
        if code:
            self.auth_code = code
            print(f"DEBUG: auth_code set to: {self.auth_code[:20]}")
            logger.info(f"DEBUG: auth_code set to: {self.auth_code[:20]}")
    
    @rx.var
    def computed_auth_url(self) -> str:
        """認証URLを計算プロパティとして生成"""
        try:
            app_id = os.getenv("THREADS_APP_ID")
            base_url = os.getenv("BASE_URL", "http://localhost:3000")
            
            if not app_id:
                return ""
            
            if base_url.startswith("http://"):
                return ""
            
            redirect_uri = f"{base_url}/auth/callback"
            scope = "threads_basic,threads_content_publish,threads_manage_insights,threads_manage_replies,threads_read_replies"
            
            return (
                f"https://threads.net/oauth/authorize?"
                f"client_id={app_id}&"
                f"redirect_uri={redirect_uri}&"
                f"scope={scope}&"
                f"response_type=code"
            )
        except:
            return ""
    

    
    def generate_auth_url(self):
        """認証URLを生成（非推奨 - computed_auth_urlを使用）"""
        try:
            app_id = os.getenv("THREADS_APP_ID")
            base_url = os.getenv("BASE_URL", "http://localhost:3000")
            
            if not app_id:
                self.error_message = "THREADS_APP_IDが設定されていません"
                return
            
            # http://の場合は警告を表示
            if base_url.startswith("http://"):
                self.error_message = "警告: HTTPでは認証できません。HTTPS環境（Renderなど）で実行してください。"
                self.auth_url = ""
                return
            
            redirect_uri = f"{base_url}/auth/callback"
            scope = "threads_basic,threads_content_publish,threads_manage_insights,threads_manage_replies,threads_read_replies"
            
            self.auth_url = (
                f"https://threads.net/oauth/authorize?"
                f"client_id={app_id}&"
                f"redirect_uri={redirect_uri}&"
                f"scope={scope}&"
                f"response_type=code"
            )
        except Exception as e:
            self.error_message = f"URL生成エラー: {str(e)}"
    
    def set_auth_code(self, code: str):
        """認証コードを設定"""
        print(f"DEBUG: set_auth_code called with: {code[:20] if code else 'None'}", flush=True)
        self.auth_code = code
        self.debug_log = f"auth_code set: {code[:20] if code else 'None'}"
    
    account_name: str = ""
    
    def set_account_name(self, name: str):
        self.account_name = name
    
    def set_user_id(self, uid: str):
        self.user_id = uid
    

    def manual_register_account(self):
        """手動でアカウントを登録"""
        import logging
        import sys
        from ..models.base import get_db
        from ..models.account import Account
        from ..services.account_service import AccountService
        from datetime import datetime, timedelta
        
        logger = logging.getLogger(__name__)
        print("DEBUG: === manual_register_account called ===", flush=True)
        sys.stdout.flush()
        print(f"DEBUG: auth_code: {self.auth_code[:20] if self.auth_code else 'None'}", flush=True)
        print(f"DEBUG: user_id: {self.user_id}", flush=True)
        print(f"DEBUG: account_name: {self.account_name}", flush=True)
        sys.stdout.flush()
        logger.info("DEBUG: === manual_register_account called ===")
        logger.info(f"DEBUG: auth_code: {self.auth_code[:20] if self.auth_code else 'None'}")
        logger.info(f"DEBUG: user_id: {self.user_id}")
        logger.info(f"DEBUG: account_name: {self.account_name}")
        
        if not self.auth_code:
            print("DEBUG: No auth_code provided", flush=True)
            sys.stdout.flush()
            logger.error("DEBUG: No auth_code provided")
            self.error_message = "認証コードがありません"
            yield
            return
        
        print("DEBUG: Starting token exchange...", flush=True)
        sys.stdout.flush()
        logger.info("DEBUG: Starting token exchange...")
        self.processing = True
        yield
        
        # トークン取得
        app_id = os.getenv("THREADS_APP_ID")
        app_secret = os.getenv("THREADS_APP_SECRET")
        base_url = os.getenv("BASE_URL", "http://localhost:3000")
        redirect_uri = f"{base_url}/auth/callback"
        
        url = "https://graph.threads.net/oauth/access_token"
        data = {
            "client_id": app_id,
            "client_secret": app_secret,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": self.auth_code
        }
        
        try:
            print(f"DEBUG: Requesting token from: {url}")
            print(f"DEBUG: Request data: client_id={app_id}, redirect_uri={redirect_uri}, code={self.auth_code[:20]}...")
            logger.info(f"DEBUG: Requesting token from: {url}")
            logger.info(f"DEBUG: Request data: client_id={app_id}, redirect_uri={redirect_uri}, code={self.auth_code[:20]}...")
            response = requests.post(url, data=data)
            print(f"DEBUG: Response status: {response.status_code}")
            logger.info(f"DEBUG: Response status: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            print(f"DEBUG: Token response: {result}")
            logger.info(f"DEBUG: Token response: {result}")
            
            access_token = result.get("access_token", "")
            threads_user_id = result.get("user_id", "")
            
            if not threads_user_id:
                logger.error("DEBUG: No user_id in response")
                self.error_message = "User IDを取得できませんでした"
                self.processing = False
                yield
                return
            
            logger.info(f"DEBUG: Token obtained for user_id: {threads_user_id}")
            logger.info(f"DEBUG: Access token length: {len(access_token)}")
            
            # アカウント名が空の場合はUser IDを使用
            account_name = self.account_name if self.account_name else f"Account_{threads_user_id[:8]}"
            logger.info(f"DEBUG: Account name: {account_name}")
            
            # アカウント登録
            db = next(get_db())
            try:
                logger.info("DEBUG: Checking for existing account...")
                existing = db.query(Account).filter_by(threads_user_id=threads_user_id).first()
                if existing:
                    logger.warning(f"DEBUG: Account already exists: {existing.name}")
                    self.error_message = f"アカウントは既に登録済みです: {existing.name}"
                    self.processing = False
                    yield
                    return
                
                logger.info("DEBUG: Creating account...")
                AccountService.create_account(
                    db=db,
                    name=account_name,
                    threads_user_id=threads_user_id,
                    access_token=access_token,
                    token_expires_at=datetime.now() + timedelta(days=60)
                )
                logger.info(f"DEBUG: Account created successfully: {account_name}")
                self.success_message = f"アカウント '{account_name}' を追加しました！"
                self.error_message = ""
                
                # フォームをリセット
                self.auth_code = ""
                self.account_name = ""
            finally:
                db.close()
                
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.json() if e.response else str(e)
            print(f"DEBUG: Token exchange failed: {error_detail}")
            logger.error(f"DEBUG: Token exchange failed: {error_detail}")
            self.error_message = f"APIエラー: {error_detail}"
        except Exception as e:
            print(f"DEBUG: Registration failed: {str(e)}")
            logger.error(f"DEBUG: Registration failed: {str(e)}", exc_info=True)
            self.error_message = f"登録エラー: {str(e)}"
        finally:
            print("DEBUG: === manual_register_account completed ===")
            logger.info("DEBUG: === manual_register_account completed ===")
            self.processing = False
            yield
    

