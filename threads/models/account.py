from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from .base import Base
import enum

class AccountStatus(enum.Enum):
    active = "active"
    inactive = "inactive"

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    threads_user_id = Column(String, unique=True, nullable=False, index=True)
    access_token = Column(String, nullable=False)
    token_expires_at = Column(DateTime, nullable=True)
    status = Column(Enum(AccountStatus), default=AccountStatus.active, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
