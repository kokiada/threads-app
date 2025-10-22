from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ..models.metrics_cache import MetricsCache, MetricType
from ..models.account import Account
from ..api.threads_client import ThreadsAPIClient
from ..services.account_service import AccountService

class MetricsService:
    MEDIA_METRICS = ["views", "likes", "replies", "reposts", "quotes", "shares"]
    USER_METRICS = ["views", "likes", "replies", "reposts", "quotes", "followers_count"]
    
    @staticmethod
    def fetch_media_metrics(db: Session, account: Account, media_id: str) -> Dict:
        decrypted_token = AccountService.get_decrypted_token(account)
        client = ThreadsAPIClient(decrypted_token)
        
        metrics = client.get_media_insights(media_id, MetricsService.MEDIA_METRICS)
        
        cache = MetricsCache(
            account_id=account.id,
            threads_media_id=media_id,
            metric_type=MetricType.media,
            metric_data=metrics
        )
        db.add(cache)
        db.commit()
        
        return metrics
    
    @staticmethod
    async def fetch_user_metrics(db: Session, account: Account, 
                                since: Optional[datetime] = None, 
                                until: Optional[datetime] = None) -> Dict:
        try:
            decrypted_token = AccountService.get_decrypted_token(account)
            client = ThreadsAPIClient(decrypted_token)
            
            since_ts = int(since.timestamp()) if since else None
            until_ts = int(until.timestamp()) if until else None
            
            metrics = client.get_user_insights(
                account.threads_user_id, 
                MetricsService.USER_METRICS, 
                since_ts, 
                until_ts
            )
            
            cache = MetricsCache(
                account_id=account.id,
                metric_type=MetricType.user,
                metric_data=metrics
            )
            db.add(cache)
            db.commit()
            
            return {"success": True, "metrics": metrics}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_cached_metrics(db: Session, account_id: int, 
                          metric_type: MetricType, 
                          media_id: Optional[str] = None) -> Optional[MetricsCache]:
        query = db.query(MetricsCache).filter(
            MetricsCache.account_id == account_id,
            MetricsCache.metric_type == metric_type
        )
        if media_id:
            query = query.filter(MetricsCache.threads_media_id == media_id)
        
        return query.order_by(MetricsCache.fetched_at.desc()).first()
    
    @staticmethod
    def calculate_growth_rate(db: Session, account_id: int, days: int = 7) -> Dict:
        since = datetime.now() - timedelta(days=days)
        
        current = db.query(MetricsCache).filter(
            MetricsCache.account_id == account_id,
            MetricsCache.metric_type == MetricType.user
        ).order_by(MetricsCache.fetched_at.desc()).first()
        
        past = db.query(MetricsCache).filter(
            MetricsCache.account_id == account_id,
            MetricsCache.metric_type == MetricType.user,
            MetricsCache.fetched_at <= since
        ).order_by(MetricsCache.fetched_at.desc()).first()
        
        if not current or not past:
            return {"growth_rate": 0, "follower_change": 0}
        
        current_followers = current.metric_data.get("followers_count", 0)
        past_followers = past.metric_data.get("followers_count", 0)
        
        follower_change = current_followers - past_followers
        growth_rate = (follower_change / past_followers * 100) if past_followers > 0 else 0
        
        return {"growth_rate": growth_rate, "follower_change": follower_change}
    
    @staticmethod
    def get_top_growing_accounts(db: Session, limit: int = 5, days: int = 7) -> List[Dict]:
        from ..models.account import Account
        accounts = db.query(Account).all()
        
        growth_data = []
        for account in accounts:
            growth = MetricsService.calculate_growth_rate(db, account.id, days)
            
            current = db.query(MetricsCache).filter(
                MetricsCache.account_id == account.id,
                MetricsCache.metric_type == MetricType.user
            ).order_by(MetricsCache.fetched_at.desc()).first()
            
            current_followers = current.metric_data.get("followers_count", 0) if current else 0
            
            growth_data.append({
                "account_id": account.id,
                "account_name": account.name,
                "growth_rate": growth["growth_rate"],
                "follower_change": growth["follower_change"],
                "current_followers": current_followers
            })
        
        return sorted(growth_data, key=lambda x: x["growth_rate"], reverse=True)[:limit]
