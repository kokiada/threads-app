import reflex as rx
from typing import List, Optional
from datetime import time
from ..models.schedule import Schedule, ScheduleType
from ..services.schedule_service import ScheduleService
from ..services.account_service import AccountService
from .base_state import BaseState
from ..scheduler import reload_schedules

class ScheduleState(BaseState):
    schedules: List[dict] = []
    accounts: List[dict] = []
    selected_account_id: int = 0
    schedule_type: str = "FIXED"
    fixed_times: str = ""
    random_start: str = "09:00"
    random_end: str = "18:00"
    random_count: int = 3
    is_active: bool = False
    
    def load_schedules(self):
        with self.get_db() as db:
            schedules = ScheduleService.get_active_schedules(db)
            self.schedules = [
                {
                    "id": s.id,
                    "account_id": s.account_id,
                    "account_name": AccountService.get_account(db, s.account_id).name,
                    "schedule_type": s.schedule_type.value,
                    "fixed_times": s.fixed_times,
                    "random_start_time": str(s.random_start_time) if s.random_start_time else "",
                    "random_end_time": str(s.random_end_time) if s.random_end_time else "",
                    "random_count": s.random_count,
                    "is_active": s.is_active,
                }
                for s in schedules
            ]
    
    def load_accounts(self):
        with self.get_db() as db:
            accounts = AccountService.get_all_accounts(db)
            self.accounts = [
                {"id": a.id, "name": a.name}
                for a in accounts
            ]
    
    def set_selected_account_id(self, value: str):
        self.selected_account_id = int(value)
    
    def set_schedule_type(self, value: str):
        self.schedule_type = value
    
    def set_fixed_times(self, value: str):
        self.fixed_times = value
    
    def set_random_start(self, value: str):
        self.random_start = value
    
    def set_random_end(self, value: str):
        self.random_end = value
    
    def set_random_count(self, value: str):
        self.random_count = int(value) if value else 0
    
    def set_is_active(self, checked: bool):
        self.is_active = checked
    
    def create_schedule(self):
        if not self.selected_account_id:
            return
        
        with self.get_db() as db:
            existing = ScheduleService.get_schedule_by_account(db, self.selected_account_id)
            if existing:
                return
            
            if self.schedule_type == "FIXED":
                times = [t.strip() for t in self.fixed_times.split(",") if t.strip()]
                ScheduleService.create_schedule(
                    db, self.selected_account_id, ScheduleType.FIXED,
                    fixed_times=times, is_active=self.is_active
                )
            else:
                start = time.fromisoformat(self.random_start)
                end = time.fromisoformat(self.random_end)
                ScheduleService.create_schedule(
                    db, self.selected_account_id, ScheduleType.RANDOM,
                    random_start_time=start, random_end_time=end,
                    random_count=self.random_count, is_active=self.is_active
                )
            
            reload_schedules()
            self.load_schedules()
    
    def toggle_schedule(self, schedule_id: int):
        with self.get_db() as db:
            ScheduleService.toggle_schedule_status(db, schedule_id)
            reload_schedules()
            self.load_schedules()
    
    def delete_schedule(self, schedule_id: int):
        with self.get_db() as db:
            ScheduleService.delete_schedule(db, schedule_id)
            reload_schedules()
            self.load_schedules()
