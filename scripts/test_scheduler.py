#!/usr/bin/env python3
"""スケジューラーのテストスクリプト"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from threads.scheduler import get_scheduler, start_scheduler, stop_scheduler, reload_schedules
from threads.models.base import get_db
from threads.services.schedule_service import ScheduleService
from threads.services.account_service import AccountService
from threads.models.schedule import ScheduleType
from datetime import time

def test_scheduler():
    print("=== スケジューラーテスト ===\n")
    
    # スケジューラー取得
    print("1. スケジューラー初期化...")
    scheduler = get_scheduler()
    print(f"   ✓ スケジューラー作成: {scheduler}")
    
    # スケジューラー起動
    print("\n2. スケジューラー起動...")
    start_scheduler()
    print(f"   ✓ 実行中: {scheduler.running}")
    
    # ジョブ一覧表示
    print("\n3. 登録済みジョブ:")
    jobs = scheduler.get_jobs()
    if jobs:
        for job in jobs:
            print(f"   - {job.id}: {job.next_run_time}")
    else:
        print("   (ジョブなし)")
    
    # データベースからアクティブなスケジュール確認
    print("\n4. アクティブなスケジュール:")
    db = next(get_db())
    try:
        schedules = ScheduleService.get_active_schedules(db)
        if schedules:
            for schedule in schedules:
                account = AccountService.get_account(db, schedule.account_id)
                print(f"   - Schedule ID: {schedule.id}")
                print(f"     Account: {account.name if account else 'Unknown'}")
                print(f"     Type: {schedule.schedule_type.value}")
                if schedule.schedule_type == ScheduleType.FIXED:
                    print(f"     Times: {schedule.fixed_times}")
                else:
                    print(f"     Random: {schedule.random_start_time} - {schedule.random_end_time} ({schedule.random_count}回)")
        else:
            print("   (アクティブなスケジュールなし)")
    finally:
        db.close()
    
    # スケジューラー停止
    print("\n5. スケジューラー停止...")
    stop_scheduler()
    print(f"   ✓ 停止完了")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_scheduler()
