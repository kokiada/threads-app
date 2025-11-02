#!/usr/bin/env python3
"""
投稿機能のテストスクリプト
Renderのログで詳細を確認するため
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from threads.models.base import get_db
from threads.services.account_service import AccountService
from threads.api.threads_client import ThreadsAPIClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_post():
    logger.info("=" * 80)
    logger.info("投稿テスト開始")
    logger.info("=" * 80)
    
    # データベースからアカウント取得
    db = next(get_db())
    try:
        accounts = AccountService.get_all_accounts(db)
        logger.info(f"アカウント数: {len(accounts)}")
        
        if not accounts:
            logger.error("アカウントが登録されていません")
            return
        
        account = accounts[0]
        logger.info(f"テスト対象アカウント: {account.name} (ID: {account.id})")
        logger.info(f"Threads User ID: {account.threads_user_id}")
        logger.info(f"ステータス: {account.status.value}")
        
        # トークン取得
        decrypted_token = AccountService.get_decrypted_token(account)
        logger.info(f"アクセストークン取得成功: {decrypted_token[:20]}...")
        
        # APIクライアント作成
        client = ThreadsAPIClient(decrypted_token)
        logger.info("APIクライアント作成成功")
        
        # レート制限確認
        logger.info("レート制限を確認中...")
        try:
            limit_info = client.get_publishing_limit(account.threads_user_id)
            logger.info(f"レート制限情報: {limit_info}")
        except Exception as e:
            logger.error(f"レート制限確認エラー: {str(e)}")
            return
        
        # テスト投稿作成
        logger.info("メディアコンテナを作成中...")
        try:
            container_id = client.create_media_container(
                account.threads_user_id,
                "TEXT",
                text="テスト投稿 from API"
            )
            logger.info(f"メディアコンテナ作成成功: {container_id}")
        except Exception as e:
            logger.error(f"メディアコンテナ作成エラー: {str(e)}")
            return
        
        # 投稿公開
        logger.info("投稿を公開中...")
        try:
            media_id = client.publish_post(account.threads_user_id, container_id)
            logger.info(f"投稿公開成功: {media_id}")
        except Exception as e:
            logger.error(f"投稿公開エラー: {str(e)}")
            return
        
        logger.info("=" * 80)
        logger.info("投稿テスト成功！")
        logger.info("=" * 80)
        
    finally:
        db.close()

if __name__ == "__main__":
    test_post()
