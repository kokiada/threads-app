from sqlalchemy import Column, Integer, String, Time, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from .base import Base
import enum

class ScheduleType(enum.Enum):
    FIXED = "FIXED"
    RANDOM = "RANDOM"

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    schedule_type = Column(Enum(ScheduleType), nullable=False)
    fixed_times = Column(JSON, nullable=True)
    random_start_time = Column(Time, nullable=True)
    random_end_time = Column(Time, nullable=True)
    random_count = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
