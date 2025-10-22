from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from .base import Base
import enum

class PostStatus(enum.Enum):
    success = "success"
    failed = "failed"

class PostHistory(Base):
    __tablename__ = "post_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="SET NULL"), nullable=True)
    threads_media_id = Column(String, nullable=True)
    posted_at = Column(DateTime, default=func.now(), nullable=False)
    status = Column(Enum(PostStatus), nullable=False)
