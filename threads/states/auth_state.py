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
    
    def generate_auth_url(self):
        """認証URLを生成"""
        try:
            # URLパラメータからcodeを取得
            code = self.router.page.params.get("code", "")
            if code:
                self.auth_code = code
                self.exchange_token()
                return
            
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
    
    def exchange_token(self):
        """認証コードをアクセストークンに交換し、自動登録"""
        if not self.auth_code:
            self.error_message = "認証コードを入力してください"
            return
        
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
            
            self.access_token = result.get("access_token", "")
            self.user_id = result.get("user_id", "")
            
            # アカウントを自動登録
            if self.access_token and self.user_id:
                self._auto_register_account()
            
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.json() if e.response else str(e)
            self.error_message = f"APIエラー: {error_detail}"
            self.success_message = ""
        except Exception as e:
            self.error_message = f"エラー: {str(e)}"
            self.success_message = ""
    
    def _auto_register_account(self):
        """アカウントを自動登録"""
        from ..models.base import get_db
        from ..models.account import Account
        from ..services.account_service import AccountService
        from datetime import datetime, timedelta
        
        db = next(get_db())
        try:
            # 既に登録済みか確認
            existing = db.query(Account).filter_by(threads_user_id=self.user_id).first()
            if existing:
                self.success_message = f"アカウント '{existing.name}' は既に登録済みです"
                self.error_message = ""
                return
            
            # アカウント名を生成
            account_name = f"Account_{self.user_id[:8]}"
            
            AccountService.create_account(
                db=db,
                name=account_name,
                threads_user_id=self.user_id,
                access_token=self.access_token,
                token_expires_at=datetime.now() + timedelta(days=60)
            )
            self.success_message = f"アカウント '{account_name}' を追加しました！"
            self.error_message = ""
            
        except Exception as e:
            self.error_message = f"登録エラー: {str(e)}"
            self.success_message = ""
        finally:
            db.close()
    
    def register_account(self):
        """アカウントを登録"""
        if not self.account_name or not self.user_id or not self.access_token:
            self.error_message = "アカウント名、User ID、アクセストークンが必要です"
            return
        
        from ..models.base import get_db
        from ..services.account_service import AccountService
        from datetime import datetime, timedelta
        
        db = next(get_db())
        try:
            AccountService.create_account(
                db=db,
                name=self.account_name,
                threads_user_id=self.user_id,
                access_token=self.access_token,
                token_expires_at=datetime.now() + timedelta(days=60)
            )
            self.success_message = f"アカウント '{self.account_name}' を登録しました！"
            return rx.redirect("/accounts")
        except Exception as e:
            self.error_message = f"登録エラー: {str(e)}"
        finally:
            db.close()
    
    def handle_callback(self):
        """コールバックURLから認証コードを自動取得"""
        # URLパラメータからcodeを取得
        code = self.router.page.params.get("code", "")
        if code:
            # #_ を除去
            code = code.split("#")[0]
            self.auth_code = code
            self.processing = True
            # トークン交換を実行
            self.exchange_token()
            self.processing = False
            # JavaScriptでリダイレクト
            return rx.redirect("/auth")
