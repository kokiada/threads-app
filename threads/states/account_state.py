import reflex as rx
from typing import List, Dict
from datetime import datetime, timedelta
from .base_state import BaseState
from ..services import AccountService
from ..models.account import AccountStatus

class AccountState(BaseState):
    accounts: List[Dict] = []
    selected_account_id: int = 0
    show_add_modal: bool = False
    
    # フォーム入力
    form_name: str = ""
    form_threads_user_id: str = ""
    form_access_token: str = ""
    
    def load_accounts(self):
        db = self.get_db()
        try:
            accounts = AccountService.get_all_accounts(db)
            self.accounts = [
                {
                    "id": acc.id,
                    "name": acc.name,
                    "threads_user_id": acc.threads_user_id,
                    "status": acc.status.value,
                    "token_expires_at": acc.token_expires_at.isoformat() if acc.token_expires_at else None,
                    "created_at": acc.created_at.isoformat(),
                }
                for acc in accounts
            ]
        finally:
            db.close()
    
    def add_account(self):
        if not self.form_name or not self.form_threads_user_id or not self.form_access_token:
            return
        
        db = self.get_db()
        try:
            AccountService.create_account(
                db,
                name=self.form_name,
                threads_user_id=self.form_threads_user_id,
                access_token=self.form_access_token,
                token_expires_at=datetime.now() + timedelta(days=60)
            )
            self.form_name = ""
            self.form_threads_user_id = ""
            self.form_access_token = ""
            self.show_add_modal = False
            self.load_accounts()
        finally:
            db.close()
    
    def delete_account(self, account_id: int):
        db = self.get_db()
        try:
            AccountService.delete_account(db, account_id)
            self.load_accounts()
        finally:
            db.close()
    
    def toggle_status(self, account_id: int):
        db = self.get_db()
        try:
            AccountService.toggle_account_status(db, account_id)
            self.load_accounts()
        finally:
            db.close()
    
    def open_add_modal(self):
        self.show_add_modal = True
    
    def close_add_modal(self):
        self.show_add_modal = False
        self.form_name = ""
        self.form_threads_user_id = ""
        self.form_access_token = ""
