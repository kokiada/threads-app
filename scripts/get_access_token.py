#!/usr/bin/env python3
"""Threads API アクセストークン取得スクリプト"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from dotenv import load_dotenv

load_dotenv()

def get_authorization_url():
    """認証URLを生成"""
    app_id = os.getenv("THREADS_APP_ID")
    redirect_uri = "https://localhost/"  # 開発用
    scope = "threads_basic,threads_content_publish,threads_manage_insights,threads_manage_replies,threads_read_replies"
    
    auth_url = (
        f"https://threads.net/oauth/authorize?"
        f"client_id={app_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"response_type=code"
    )
    
    print("=" * 80)
    print("Threads API アクセストークン取得手順")
    print("=" * 80)
    print("\n1. 以下のURLをブラウザで開いてください：")
    print(f"\n{auth_url}\n")
    print("2. Threadsアカウントでログインして承認してください")
    print("3. リダイレクト後のURL（https://localhost/?code=...）から")
    print("   'code=' の後の文字列をコピーしてください")
    print("\n" + "=" * 80)

def exchange_code_for_token(code):
    """認証コードをアクセストークンに交換"""
    app_id = os.getenv("THREADS_APP_ID")
    app_secret = os.getenv("THREADS_APP_SECRET")
    redirect_uri = "https://localhost/"
    
    url = "https://graph.threads.net/oauth/access_token"
    data = {
        "client_id": app_id,
        "client_secret": app_secret,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": code
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        result = response.json()
        
        print("\n✅ アクセストークン取得成功！")
        print("=" * 80)
        print(f"アクセストークン: {result.get('access_token')}")
        print(f"ユーザーID: {result.get('user_id')}")
        print("=" * 80)
        print("\n次のステップ:")
        print("1. Reflexアプリを起動: /home/koki/work/threads/venv/bin/reflex run")
        print("2. http://localhost:3000/accounts にアクセス")
        print("3. 「アカウント追加」で以下を入力:")
        print(f"   - 名前: 任意の名前")
        print(f"   - User ID: {result.get('user_id')}")
        print(f"   - アクセストークン: {result.get('access_token')}")
        print("\n" + "=" * 80)
        
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ エラー: {e}")
        if hasattr(e.response, 'text'):
            print(f"詳細: {e.response.text}")
        return None

def main():
    print("\nThreads API アクセストークン取得ツール\n")
    
    if len(sys.argv) > 1:
        # コマンドライン引数でコードが渡された場合
        code = sys.argv[1]
        exchange_code_for_token(code)
    else:
        # 認証URLを表示
        get_authorization_url()
        print("\n認証コードを取得したら、以下のコマンドを実行してください:")
        print(f"python {sys.argv[0]} <認証コード>")
        print("\n例:")
        print(f"python {sys.argv[0]} AQBxxx...\n")

if __name__ == "__main__":
    main()
