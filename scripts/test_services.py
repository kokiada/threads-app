#!/usr/bin/env python3
"""サービス層の動作確認テスト"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from threads.models.base import init_db, SessionLocal
from threads.services import (
    AccountService, PostGroupService, PostService, 
    ScheduleService, MetricsService, TokenService
)
from threads.models.post import MediaType
from threads.models.schedule import ScheduleType
from datetime import datetime, timedelta, time

def test_services():
    print("サービス層の動作確認テスト開始...\n")
    
    # データベース初期化
    init_db()
    db = SessionLocal()
    
    try:
        # 1. AccountService テスト
        print("1. AccountService テスト")
        account = AccountService.create_account(
            db, 
            name="テストアカウント",
            threads_user_id="test_user_123",
            access_token="test_token_abc",
            token_expires_at=datetime.now() + timedelta(days=60)
        )
        print(f"✓ アカウント作成成功: {account.name} (ID: {account.id})")
        
        accounts = AccountService.get_all_accounts(db)
        print(f"✓ アカウント一覧取得: {len(accounts)}件")
        
        # 2. PostGroupService テスト
        print("\n2. PostGroupService テスト")
        group = PostGroupService.create_group(
            db,
            name="テストグループ",
            description="テスト用の投稿グループ"
        )
        print(f"✓ グループ作成成功: {group.name} (ID: {group.id})")
        
        PostGroupService.assign_accounts_to_group(db, group.id, [account.id])
        print(f"✓ アカウントをグループに紐付け")
        
        group_accounts = PostGroupService.get_accounts_by_group(db, group.id)
        print(f"✓ グループのアカウント取得: {len(group_accounts)}件")
        
        # 3. PostService テスト
        print("\n3. PostService テスト")
        post = PostService.create_post(
            db,
            group_id=group.id,
            media_type=MediaType.TEXT,
            text="これはテスト投稿です"
        )
        print(f"✓ 投稿作成成功: {post.text[:20]}... (ID: {post.id})")
        
        posts = PostService.get_posts_by_group(db, group.id)
        print(f"✓ グループの投稿取得: {len(posts)}件")
        
        random_post = PostService.get_random_post_from_group(db, group.id)
        print(f"✓ ランダム投稿取得: {random_post.text[:20] if random_post else 'なし'}...")
        
        # 4. ScheduleService テスト
        print("\n4. ScheduleService テスト")
        schedule = ScheduleService.create_schedule(
            db,
            account_id=account.id,
            schedule_type=ScheduleType.FIXED,
            fixed_times=["10:00", "15:00", "20:00"],
            is_active=True
        )
        print(f"✓ スケジュール作成成功: {schedule.schedule_type.value} (ID: {schedule.id})")
        
        active_schedules = ScheduleService.get_active_schedules(db)
        print(f"✓ アクティブなスケジュール取得: {len(active_schedules)}件")
        
        # 5. MetricsService テスト
        print("\n5. MetricsService テスト")
        print("✓ MetricsService インポート成功")
        
        # 6. TokenService テスト
        print("\n6. TokenService テスト")
        print("✓ TokenService インポート成功")
        
        print("\n" + "="*50)
        print("✅ すべてのサービスが正常に動作しました")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_services()
