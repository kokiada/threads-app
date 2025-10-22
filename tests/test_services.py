import pytest
from datetime import datetime, timedelta
from threads.services.account_service import AccountService
from threads.services.post_group_service import PostGroupService
from threads.services.post_service import PostService
from threads.services.schedule_service import ScheduleService

class TestAccountService:
    def test_create_account(self, test_db):
        """アカウント作成のテスト"""
        account = AccountService.create_account(
            test_db,
            name="テストアカウント",
            threads_user_id="test_user_123",
            access_token="test_token",
            token_expires_at=datetime.now() + timedelta(days=60)
        )
        assert account.id is not None
        assert account.name == "テストアカウント"
        assert account.threads_user_id == "test_user_123"
        assert account.status.value == "active"
    
    def test_get_account(self, test_db):
        """アカウント取得のテスト"""
        account = AccountService.create_account(
            test_db,
            name="テストアカウント",
            threads_user_id="test_user_123",
            access_token="test_token",
            token_expires_at=datetime.now() + timedelta(days=60)
        )
        retrieved = AccountService.get_account(test_db, account.id)
        assert retrieved.id == account.id
        assert retrieved.name == account.name
    
    def test_get_all_accounts(self, test_db):
        """アカウント一覧取得のテスト"""
        AccountService.create_account(
            test_db, "アカウント1", "user1", "token1",
            datetime.now() + timedelta(days=60)
        )
        AccountService.create_account(
            test_db, "アカウント2", "user2", "token2",
            datetime.now() + timedelta(days=60)
        )
        accounts = AccountService.get_all_accounts(test_db)
        assert len(accounts) == 2

class TestPostGroupService:
    def test_create_group(self, test_db):
        """グループ作成のテスト"""
        group = PostGroupService.create_group(
            test_db,
            name="テストグループ",
            description="テスト用のグループ"
        )
        assert group.id is not None
        assert group.name == "テストグループ"
    
    def test_assign_accounts_to_group(self, test_db):
        """アカウントのグループ紐付けテスト"""
        account = AccountService.create_account(
            test_db, "アカウント", "user1", "token1",
            datetime.now() + timedelta(days=60)
        )
        group = PostGroupService.create_group(test_db, "グループ")
        PostGroupService.assign_accounts_to_group(test_db, group.id, [account.id])
        accounts = PostGroupService.get_accounts_by_group(test_db, group.id)
        assert len(accounts) == 1
        assert accounts[0].id == account.id

class TestPostService:
    def test_create_post(self, test_db):
        """投稿作成のテスト"""
        group = PostGroupService.create_group(test_db, "グループ")
        post = PostService.create_post(
            test_db,
            group_id=group.id,
            media_type="TEXT",
            text="テスト投稿"
        )
        assert post.id is not None
        assert post.text == "テスト投稿"
        assert post.media_type.value == "TEXT"
    
    def test_get_random_post(self, test_db):
        """ランダム投稿取得のテスト"""
        group = PostGroupService.create_group(test_db, "グループ")
        PostService.create_post(test_db, group.id, "TEXT", "投稿1")
        PostService.create_post(test_db, group.id, "TEXT", "投稿2")
        random_post = PostService.get_random_post_from_group(test_db, group.id)
        assert random_post is not None
        assert random_post.text in ["投稿1", "投稿2"]

class TestScheduleService:
    def test_create_schedule(self, test_db):
        """スケジュール作成のテスト"""
        account = AccountService.create_account(
            test_db, "アカウント", "user1", "token1",
            datetime.now() + timedelta(days=60)
        )
        schedule = ScheduleService.create_schedule(
            test_db,
            account_id=account.id,
            schedule_type="FIXED",
            fixed_times=["10:00", "15:00"]
        )
        assert schedule.id is not None
        assert schedule.schedule_type.value == "FIXED"
        assert schedule.fixed_times == ["10:00", "15:00"]
    
    def test_get_active_schedules(self, test_db):
        """アクティブなスケジュール取得のテスト"""
        account = AccountService.create_account(
            test_db, "アカウント", "user1", "token1",
            datetime.now() + timedelta(days=60)
        )
        schedule = ScheduleService.create_schedule(
            test_db, account.id, "FIXED", ["10:00"]
        )
        ScheduleService.toggle_schedule_status(test_db, schedule.id)
        active = ScheduleService.get_active_schedules(test_db)
        assert len(active) == 1
        assert active[0].is_active == True
