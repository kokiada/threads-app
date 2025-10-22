from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import time
from ..models.schedule import Schedule, ScheduleType

class ScheduleService:
    @staticmethod
    def create_schedule(db: Session, account_id: int, schedule_type: ScheduleType,
                       fixed_times: Optional[List[str]] = None,
                       random_start_time: Optional[time] = None,
                       random_end_time: Optional[time] = None,
                       random_count: Optional[int] = None,
                       is_active: bool = False) -> Schedule:
        schedule = Schedule(
            account_id=account_id,
            schedule_type=schedule_type,
            fixed_times=fixed_times,
            random_start_time=random_start_time,
            random_end_time=random_end_time,
            random_count=random_count,
            is_active=is_active
        )
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        return schedule
    
    @staticmethod
    def get_schedule_by_account(db: Session, account_id: int) -> Optional[Schedule]:
        return db.query(Schedule).filter(Schedule.account_id == account_id).first()
    
    @staticmethod
    def update_schedule(db: Session, schedule_id: int, 
                       fixed_times: Optional[List[str]] = None,
                       random_start_time: Optional[time] = None,
                       random_end_time: Optional[time] = None,
                       random_count: Optional[int] = None) -> Optional[Schedule]:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            return None
        
        if fixed_times is not None:
            schedule.fixed_times = fixed_times
        if random_start_time is not None:
            schedule.random_start_time = random_start_time
        if random_end_time is not None:
            schedule.random_end_time = random_end_time
        if random_count is not None:
            schedule.random_count = random_count
        
        db.commit()
        db.refresh(schedule)
        return schedule
    
    @staticmethod
    def delete_schedule(db: Session, schedule_id: int) -> bool:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            return False
        db.delete(schedule)
        db.commit()
        return True
    
    @staticmethod
    def toggle_schedule_status(db: Session, schedule_id: int) -> Optional[Schedule]:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            return None
        
        schedule.is_active = not schedule.is_active
        db.commit()
        db.refresh(schedule)
        return schedule
    
    @staticmethod
    def get_active_schedules(db: Session) -> List[Schedule]:
        return db.query(Schedule).filter(Schedule.is_active == True).all()
