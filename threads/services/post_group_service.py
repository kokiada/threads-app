from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.post_group import PostGroup
from ..models.account_group import AccountGroup
from ..models.account import Account

class PostGroupService:
    @staticmethod
    def create_group(db: Session, name: str, description: Optional[str] = None) -> PostGroup:
        group = PostGroup(name=name, description=description)
        db.add(group)
        db.commit()
        db.refresh(group)
        return group
    
    @staticmethod
    def get_group(db: Session, group_id: int) -> Optional[PostGroup]:
        return db.query(PostGroup).filter(PostGroup.id == group_id).first()
    
    @staticmethod
    def get_all_groups(db: Session, limit: int = 100, offset: int = 0) -> List[PostGroup]:
        return db.query(PostGroup).offset(offset).limit(limit).all()
    
    @staticmethod
    def update_group(db: Session, group_id: int, name: Optional[str] = None, 
                    description: Optional[str] = None) -> Optional[PostGroup]:
        group = db.query(PostGroup).filter(PostGroup.id == group_id).first()
        if not group:
            return None
        
        if name:
            group.name = name
        if description is not None:
            group.description = description
        
        db.commit()
        db.refresh(group)
        return group
    
    @staticmethod
    def delete_group(db: Session, group_id: int) -> bool:
        group = db.query(PostGroup).filter(PostGroup.id == group_id).first()
        if not group:
            return False
        db.delete(group)
        db.commit()
        return True
    
    @staticmethod
    def assign_accounts_to_group(db: Session, group_id: int, account_ids: List[int]) -> bool:
        group = db.query(PostGroup).filter(PostGroup.id == group_id).first()
        if not group:
            return False
        
        for account_id in account_ids:
            existing = db.query(AccountGroup).filter(
                AccountGroup.group_id == group_id,
                AccountGroup.account_id == account_id
            ).first()
            if not existing:
                db.add(AccountGroup(account_id=account_id, group_id=group_id))
        
        db.commit()
        return True
    
    @staticmethod
    def remove_accounts_from_group(db: Session, group_id: int, account_ids: List[int]) -> bool:
        db.query(AccountGroup).filter(
            AccountGroup.group_id == group_id,
            AccountGroup.account_id.in_(account_ids)
        ).delete(synchronize_session=False)
        db.commit()
        return True
    
    @staticmethod
    def get_accounts_by_group(db: Session, group_id: int) -> List[Account]:
        return db.query(Account).join(AccountGroup).filter(
            AccountGroup.group_id == group_id
        ).all()
    
    @staticmethod
    def get_groups_by_account(db: Session, account_id: int) -> List[PostGroup]:
        return db.query(PostGroup).join(AccountGroup).filter(
            AccountGroup.account_id == account_id
        ).all()
