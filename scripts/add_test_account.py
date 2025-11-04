#!/usr/bin/env python3
"""テスト用アカウントを直接DBに追加"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from threads.models.base import get_db
from threads.services.account_service import AccountService
from datetime import datetime, timedelta

def add_test_account():
    """テスト用のダミーアカウントを追加"""
    db = next(get_db())
    try:
        # ダミーのアクセストークンとユーザーID
        test_accounts = [
            {
                "name": "Test Account 1",
                "threads_user_id": "test_user_123456",
                "access_token": "dummy_token_for_testing_only",
                "token_expires_at": datetime.now() + timedelta(days=60)
            },
            {
                "name": "Test Account 2", 
                "threads_user_id": "test_user_789012",
                "access_token": "dummy_token_for_testing_only_2",
                "token_expires_at": datetime.now() + timedelta(days=60)
            }
        ]
        
        for acc in test_accounts:
            try:
                account = AccountService.create_account(
                    db=db,
                    name=acc["name"],
                    threads_user_id=acc["threads_user_id"],
                    access_token=acc["access_token"],
                    token_expires_at=acc["token_expires_at"]
                )
                print(f"✅ 追加: {acc['name']} (ID: {account.id})")
            except Exception as e:
                print(f"⚠️  スキップ: {acc['name']} - {str(e)}")
        
        print("\n✅ テストアカウントの追加完了")
        print("📝 注意: これらはダミーアカウントで、実際のThreads APIは使用できません")
        
    finally:
        db.close()

if __name__ == "__main__":
    add_test_account()
