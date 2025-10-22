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
    
    def generate_auth_url(self):
        """認証URLを生成"""
        app_id = os.getenv("THREADS_APP_ID")
        redirect_uri = "http://localhost:3000/auth/callback"
        scope = "threads_basic,threads_content_publish,threads_manage_insights,threads_manage_replies,threads_read_replies"
        
        self.auth_url = (
            f"https://threads.net/oauth/authorize?"
            f"client_id={app_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scope}&"
            f"response_type=code"
        )
    
    def set_auth_code(self, code: str):
        """認証コードを設定"""
        self.auth_code = code
    
    def exchange_token(self):
        """認証コードをアクセストークンに交換"""
        if not self.auth_code:
            self.error_message = "認証コードを入力してください"
            return
        
        app_id = os.getenv("THREADS_APP_ID")
        app_secret = os.getenv("THREADS_APP_SECRET")
        redirect_uri = "http://localhost:3000/auth/callback"
        
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
            self.success_message = "アクセストークン取得成功！"
            self.error_message = ""
            
        except Exception as e:
            self.error_message = f"エラー: {str(e)}"
            self.success_message = ""
