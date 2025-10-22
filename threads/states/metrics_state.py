import reflex as rx
from typing import List
from datetime import datetime, timedelta
from ..services.account_service import AccountService
from ..services.metrics_service import MetricsService
from .base_state import BaseState

class MetricsState(BaseState):
    accounts: List[dict] = []
    top_accounts: List[dict] = []
    selected_account_id: int = 0
    account_metrics: dict = {}
    loading: bool = False
    
    def load_accounts(self):
        with self.get_db() as db:
            accounts = AccountService.get_all_accounts(db)
            self.accounts = [
                {"id": a.id, "name": a.name}
                for a in accounts
            ]
    
    def load_top_accounts(self):
        with self.get_db() as db:
            top = MetricsService.get_top_growing_accounts(db, limit=10)
            self.top_accounts = [
                {
                    "account_name": t["account_name"],
                    "growth_rate": f"{t['growth_rate']:.2f}%",
                    "followers": t["current_followers"],
                }
                for t in top
            ]
    
    def set_selected_account_id(self, value: str):
        self.selected_account_id = int(value)
    
    async def fetch_metrics(self):
        if not self.selected_account_id:
            return
        
        self.loading = True
        
        with self.get_db() as db:
            account = AccountService.get_account(db, self.selected_account_id)
            if not account:
                self.loading = False
                return
            
            since = datetime.now() - timedelta(days=30)
            until = datetime.now()
            
            result = await MetricsService.fetch_user_metrics(
                db, account, since, until
            )
            
            if result.get("success"):
                metrics = result.get("metrics", {})
                self.account_metrics = {
                    "views": metrics.get("views", 0),
                    "likes": metrics.get("likes", 0),
                    "replies": metrics.get("replies", 0),
                    "reposts": metrics.get("reposts", 0),
                    "followers_count": metrics.get("followers_count", 0),
                }
            else:
                self.account_metrics = {}
        
        self.loading = False
