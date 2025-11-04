#!/usr/bin/env python3
"""実際のThreads APIアクセストークンでアカウントを追加"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from threads.models.base import get_db
from threads.services.account_service import AccountService
from datetime import datetime, timedelta
import requests

def exchange_token(short_token: str) -> str:
    """短期トークンを長期トークンに交換"""
    app_id = os.getenv("THREADS_APP_ID")
    app_secret = os.getenv("THREADS_APP_SECRET")
    
    print("🔄 短期トークンを長期トークンに交換中...")
    
    try:
        response = requests.get(
            "https://graph.threads.net/access_token",
            params={
                "grant_type": "th_exchange_token",
                "client_secret": app_secret,
                "access_token": short_token
            }
        )
        response.raise_for_status()
        data = response.json()
        
        long_token = data.get("access_token")
        expires_in = data.get("expires_in", 5184000)  # 60日
        
        print(f"✅ 長期トークン取得成功 (有効期限: {expires_in // 86400}日)")
        return long_token
        
    except Exception as e:
        print(f"⚠️  トークン交換失敗: {str(e)}")
        print("💡 短期トークンをそのまま使用します")
        return short_token

def add_real_account(access_token: str, account_name: str = ""):
    """実際のアクセストークンでアカウントを追加"""
    from dotenv import load_dotenv
    load_dotenv()
    
    print(f"🔑 アクセストークン: {access_token[:20]}...")
    
    # 短期トークンを長期トークンに交換
    access_token = exchange_token(access_token)
    
    # トークンからユーザーIDを取得
    print("📡 ユーザー情報を取得中...")
    try:
        response = requests.get(
            "https://graph.threads.net/v1.0/me",
            params={
                "fields": "id,username,name",
                "access_token": access_token
            }
        )
        response.raise_for_status()
        user_data = response.json()
        
        user_id = user_data.get("id")
        username = user_data.get("username")
        name = user_data.get("name")
        
        print(f"✅ ユーザー情報取得成功:")
        print(f"   ID: {user_id}")
        print(f"   Username: @{username}")
        print(f"   Name: {name}")
        
    except Exception as e:
        print(f"❌ エラー: ユーザー情報の取得に失敗しました")
        print(f"   {str(e)}")
        return
    
    # アカウント名を決定
    if not account_name:
        account_name = name or username or f"Account_{user_id[:8]}"
    
    # DBに追加
    print(f"\n💾 アカウントをDBに追加中...")
    db = next(get_db())
    try:
        account = AccountService.create_account(
            db=db,
            name=account_name,
            threads_user_id=user_id,
            access_token=access_token,
            token_expires_at=datetime.now() + timedelta(days=60)
        )
        print(f"✅ アカウント追加成功!")
        print(f"   ID: {account.id}")
        print(f"   名前: {account.name}")
        print(f"   Threads User ID: {account.threads_user_id}")
        print(f"   トークン有効期限: {account.token_expires_at}")
        
    except Exception as e:
        print(f"❌ エラー: アカウントの追加に失敗しました")
        print(f"   {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python scripts/add_real_account.py <ACCESS_TOKEN> [アカウント名]")
        print("")
        print("例:")
        print("  python scripts/add_real_account.py 'IGQWRN...' 'My Account'")
        print("")
        print("アクセストークンの取得方法:")
        print("  1. https://developers.facebook.com/apps/ でアプリを選択")
        print("  2. Threads > 設定 > アクセストークン")
        print("  3. 長期トークンを生成")
        sys.exit(1)
    
    access_token = sys.argv[1]
    account_name = sys.argv[2] if len(sys.argv) > 2 else ""
    
    add_real_account(access_token, account_name)
