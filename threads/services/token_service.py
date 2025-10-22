from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List
from ..models.account import Account
from ..api.threads_client import ThreadsAPIClient
from ..services.account_service import AccountService
from ..utils.exceptions import TokenExpiredError

class TokenService:
    @staticmethod
    def refresh_token(db: Session, account: Account) -> Dict:
        try:
            decrypted_token = AccountService.get_decrypted_token(account)
            client = ThreadsAPIClient(decrypted_token)
            
            result = client.refresh_access_token()
            new_token = result.get("access_token")
            expires_in = result.get("expires_in", 5184000)  # デフォルト60日
            
            if new_token:
                new_expires_at = datetime.now() + timedelta(seconds=expires_in)
                AccountService.update_account(
                    db, account.id, 
                    access_token=new_token, 
                    token_expires_at=new_expires_at
                )
                return {"success": True, "expires_at": new_expires_at}
            
            return {"success": False, "error": "No token returned"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def refresh_expiring_tokens(db: Session, days_before: int = 7) -> List[Dict]:
        accounts = AccountService.get_accounts_needing_token_refresh(db, days_before)
        results = []
        
        for account in accounts:
            result = TokenService.refresh_token(db, account)
            results.append({
                "account_id": account.id,
                "account_name": account.name,
                "result": result
            })
        
        return results
