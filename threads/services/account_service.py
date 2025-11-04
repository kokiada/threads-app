from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from ..models.account import Account, AccountStatus
from ..models.base import get_db
from ..utils.crypto import encrypt_token, decrypt_token
from ..utils.exceptions import ValidationError

class AccountService:
    @staticmethod
    def create_account(db: Session, name: str, threads_user_id: str, access_token: str, 
                      token_expires_at: Optional[datetime] = None) -> Account:
        existing = db.query(Account).filter(Account.threads_user_id == threads_user_id).first()
        if existing:
            raise ValidationError(f"アカウント '{existing.name}' は既に登録されています")
        
        encrypted_token = encrypt_token(access_token)
        account = Account(
            name=name,
            threads_user_id=threads_user_id,
            access_token=encrypted_token,
            token_expires_at=token_expires_at,
            status=AccountStatus.active
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        return account
    
    @staticmethod
    def get_account(db: Session, account_id: int) -> Optional[Account]:
        return db.query(Account).filter(Account.id == account_id).first()
    
    @staticmethod
    def get_all_accounts(db: Session, status: Optional[AccountStatus] = None, 
                        limit: int = 100, offset: int = 0) -> List[Account]:
        query = db.query(Account)
        if status:
            query = query.filter(Account.status == status)
        return query.offset(offset).limit(limit).all()
    
    @staticmethod
    def update_account(db: Session, account_id: int, name: Optional[str] = None,
                      access_token: Optional[str] = None, 
                      token_expires_at: Optional[datetime] = None) -> Optional[Account]:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            return None
        
        if name:
            account.name = name
        if access_token:
            account.access_token = encrypt_token(access_token)
        if token_expires_at:
            account.token_expires_at = token_expires_at
        
        db.commit()
        db.refresh(account)
        return account
    
    @staticmethod
    def delete_account(db: Session, account_id: int) -> bool:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            return False
        db.delete(account)
        db.commit()
        return True
    
    @staticmethod
    def toggle_account_status(db: Session, account_id: int) -> Optional[Account]:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            return None
        
        account.status = AccountStatus.inactive if account.status == AccountStatus.active else AccountStatus.active
        db.commit()
        db.refresh(account)
        return account
    
    @staticmethod
    def get_accounts_needing_token_refresh(db: Session, days_before: int = 7) -> List[Account]:
        threshold = datetime.now() + timedelta(days=days_before)
        return db.query(Account).filter(
            Account.status == AccountStatus.active,
            Account.token_expires_at <= threshold
        ).all()
    
    @staticmethod
    def get_decrypted_token(account: Account) -> str:
        return decrypt_token(account.access_token)
