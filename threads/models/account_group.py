from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from .base import Base

class AccountGroup(Base):
    __tablename__ = "account_groups"
    
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(Integer, ForeignKey("post_groups.id", ondelete="CASCADE"), nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('account_id', 'group_id'),
    )
