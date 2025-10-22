from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime, time, timedelta
import random
import asyncio
from typing import Optional
from sqlalchemy.orm import Session
from ..models.base import get_db
from ..models.schedule import Schedule, ScheduleType
from ..services.schedule_service import ScheduleService
from ..services.account_service import AccountService
from ..services.posting_service import PostingService
from ..services.token_service import TokenService
from ..services.post_group_service import PostGroupService
from ..utils.logger import logger
import os

# グローバルスケジューラーインスタンス
_scheduler: Optional[BackgroundScheduler] = None

def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./threads.db")
        
        jobstores = {
            'default': SQLAlchemyJobStore(url=database_url)
        }
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        _scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )
    return _scheduler

def execute_scheduled_post(account_id: int, schedule_id: int):
    """スケジュールされた投稿を実行"""
    logger.info(f"Executing scheduled post for account_id={account_id}, schedule_id={schedule_id}")
    db = next(get_db())
    try:
        account = AccountService.get_account(db, account_id)
        if not account or account.status.value != "active":
            logger.warning(f"Account {account_id} not found or inactive")
            return
        
        schedule = ScheduleService.get_schedule_by_account(db, account_id)
        if not schedule or not schedule.is_active:
            logger.warning(f"Schedule for account {account_id} not found or inactive")
            return
        
        groups = PostGroupService.get_groups_by_account(db, account_id)
        if not groups:
            logger.warning(f"No groups found for account {account_id}")
            return
        
        group = random.choice(groups)
        logger.info(f"Selected group {group.name} for account {account.name}")
        
        asyncio.run(PostingService.post_random(db, account, group.id))
    except Exception as e:
        logger.error(f"Error executing scheduled post: {str(e)}")
    finally:
        db.close()

def token_refresh_job():
    """トークンリフレッシュジョブ（毎日実行）"""
    logger.info("Starting token refresh job")
    db = next(get_db())
    try:
        results = TokenService.refresh_expiring_tokens(db, days_before=7)
        logger.info(f"Token refresh completed: {len(results)} accounts processed")
    except Exception as e:
        logger.error(f"Error in token refresh job: {str(e)}")
    finally:
        db.close()

def reload_schedules():
    """アクティブなスケジュールを再読み込み"""
    scheduler = get_scheduler()
    db = next(get_db())
    
    try:
        # 既存のスケジュールジョブを削除
        for job in scheduler.get_jobs():
            if job.id.startswith("schedule_"):
                job.remove()
        
        # アクティブなスケジュールを取得
        schedules = ScheduleService.get_active_schedules(db)
        
        for schedule in schedules:
            if schedule.schedule_type == ScheduleType.FIXED and schedule.fixed_times:
                # 固定時刻スケジュール
                for time_str in schedule.fixed_times:
                    hour, minute = map(int, time_str.split(":"))
                    scheduler.add_job(
                        execute_scheduled_post,
                        'cron',
                        hour=hour,
                        minute=minute,
                        args=[schedule.account_id, schedule.id],
                        id=f"schedule_{schedule.id}_{time_str}",
                        replace_existing=True
                    )
            
            elif schedule.schedule_type == ScheduleType.RANDOM:
                # ランダム時刻スケジュール
                if schedule.random_count and schedule.random_start_time and schedule.random_end_time:
                    # 1日の開始時刻にランダム投稿をスケジュール
                    scheduler.add_job(
                        schedule_random_posts,
                        'cron',
                        hour=schedule.random_start_time.hour,
                        minute=schedule.random_start_time.minute,
                        args=[schedule.account_id, schedule.id, schedule.random_count,
                              schedule.random_start_time, schedule.random_end_time],
                        id=f"schedule_random_{schedule.id}",
                        replace_existing=True
                    )
    
    finally:
        db.close()

def schedule_random_posts(account_id: int, schedule_id: int, count: int, 
                         start_time: time, end_time: time):
    """ランダム時刻に投稿をスケジュール"""
    scheduler = get_scheduler()
    
    # 開始時刻と終了時刻の間でランダムな時刻を生成
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    
    if end_minutes <= start_minutes:
        end_minutes += 24 * 60
    
    random_times = sorted(random.sample(range(start_minutes, end_minutes), min(count, end_minutes - start_minutes)))
    
    for i, minutes in enumerate(random_times):
        hour = (minutes // 60) % 24
        minute = minutes % 60
        run_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if run_time < datetime.now():
            run_time += timedelta(days=1)
        
        scheduler.add_job(
            execute_scheduled_post,
            'date',
            run_date=run_time,
            args=[account_id, schedule_id],
            id=f"random_post_{schedule_id}_{i}",
            replace_existing=True
        )

def start_scheduler():
    """スケジューラーを開始"""
    logger.info("Starting scheduler")
    scheduler = get_scheduler()
    
    if not scheduler.running:
        scheduler.add_job(
            token_refresh_job,
            'cron',
            hour=3,
            minute=0,
            id='token_refresh',
            replace_existing=True
        )
        
        reload_schedules()
        scheduler.start()
        logger.info("Scheduler started successfully")
    else:
        logger.warning("Scheduler already running")

def stop_scheduler():
    """スケジューラーを停止"""
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown()
