from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from .base import Base
import enum

class MetricType(enum.Enum):
    media = "media"
    user = "user"

class MetricsCache(Base):
    __tablename__ = "metrics_cache"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    threads_media_id = Column(String, nullable=True)
    metric_type = Column(Enum(MetricType), nullable=False)
    metric_data = Column(JSON, nullable=False)
    fetched_at = Column(DateTime, default=func.now(), nullable=False)
