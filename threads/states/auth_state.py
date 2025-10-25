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
    
    def extract_code_from_url(self):
        """ページ読み込み時にURLからcodeを抽出"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            code = self.router.page.params.get("code", "")
            logger.info(f"extract_code_from_url - code: {code[:20] if code else 'None'}")
            
            if code:
                self.auth_code = code
                logger.info(f"Code extracted from URL: {code[:20]}")
        except Exception as e:
            logger.error(f"Error extracting code: {str(e)}", exc_info=True)
    
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
        self.auth_code = code
    
    account_name: str = ""
    
    def set_account_name(self, name: str):
        self.account_name = name
    
    def set_user_id(self, uid: str):
        self.user_id = uid
    

    
    def manual_register_account(self):
        """手動でアカウントを登録"""
        import logging
        from ..models.base import get_db
        from ..models.account import Account
        from ..services.account_service import AccountService
        from datetime import datetime, timedelta
        
        logger = logging.getLogger(__name__)
        
        if not self.account_name or not self.user_id:
            self.error_message = "アカウント名とUser IDを入力してください"
            return
        
        if not self.auth_code:
            self.error_message = "認証コードがありません"
            return
        
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
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()
            
            access_token = result.get("access_token", "")
            logger.info(f"Token obtained for user_id: {self.user_id}")
            
            # アカウント登録
            db = next(get_db())
            try:
                existing = db.query(Account).filter_by(threads_user_id=self.user_id).first()
                if existing:
                    self.error_message = f"アカウントは既に登録済みです: {existing.name}"
                    return
                
                AccountService.create_account(
                    db=db,
                    name=self.account_name,
                    threads_user_id=self.user_id,
                    access_token=access_token,
                    token_expires_at=datetime.now() + timedelta(days=60)
                )
                logger.info(f"Account created: {self.account_name}")
                self.success_message = f"アカウント '{self.account_name}' を追加しました！"
                self.error_message = ""
            finally:
                db.close()
                
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.json() if e.response else str(e)
            logger.error(f"Token exchange failed: {error_detail}")
            self.error_message = f"APIエラー: {error_detail}"
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}", exc_info=True)
            self.error_message = f"登録エラー: {str(e)}"
        finally:
            self.processing = False
            yield
    

