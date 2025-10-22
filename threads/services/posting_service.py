from sqlalchemy.orm import Session
import asyncio
import time
from typing import Optional, List, Dict
from ..models.post import Post, MediaType
from ..models.account import Account
from ..models.post_history import PostHistory, PostStatus
from ..api.threads_client import ThreadsAPIClient
from ..services.account_service import AccountService
from ..utils.exceptions import ThreadsAPIError, RateLimitError

class PostingService:
    @staticmethod
    async def post_single(db: Session, account: Account, post: Post) -> Dict:
        try:
            decrypted_token = AccountService.get_decrypted_token(account)
            client = ThreadsAPIClient(decrypted_token)
            
            # レート制限チェック
            limit_info = client.get_publishing_limit(account.threads_user_id)
            if limit_info.get("quota_usage", 0) >= 250:
                raise RateLimitError("Daily posting limit reached")
            
            # メディアコンテナ作成
            container_id = None
            if post.media_type == MediaType.TEXT:
                container_id = client.create_media_container(
                    account.threads_user_id, "TEXT", text=post.text
                )
            elif post.media_type == MediaType.IMAGE:
                container_id = client.create_media_container(
                    account.threads_user_id, "IMAGE", 
                    text=post.text, image_url=post.media_urls[0] if post.media_urls else None
                )
            elif post.media_type == MediaType.VIDEO:
                container_id = client.create_media_container(
                    account.threads_user_id, "VIDEO",
                    text=post.text, video_url=post.media_urls[0] if post.media_urls else None
                )
            elif post.media_type == MediaType.CAROUSEL:
                children = []
                for url in post.media_urls or []:
                    child_id = client.create_media_container(
                        account.threads_user_id, "IMAGE", image_url=url
                    )
                    children.append(child_id)
                container_id = client.create_media_container(
                    account.threads_user_id, "CAROUSEL", text=post.text, children=children
                )
            
            # 30秒待機（画像/動画の場合）
            if post.media_type in [MediaType.IMAGE, MediaType.VIDEO, MediaType.CAROUSEL]:
                await asyncio.sleep(30)
            
            # 投稿公開
            media_id = client.publish_post(account.threads_user_id, container_id)
            
            # 履歴記録
            history = PostHistory(
                account_id=account.id,
                post_id=post.id,
                threads_media_id=media_id,
                status=PostStatus.success
            )
            db.add(history)
            db.commit()
            
            return {"success": True, "media_id": media_id}
        
        except Exception as e:
            history = PostHistory(
                account_id=account.id,
                post_id=post.id,
                status=PostStatus.failed
            )
            db.add(history)
            db.commit()
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def post_random(db: Session, account: Account, group_id: int) -> Dict:
        from .post_service import PostService
        post = PostService.get_random_post_from_group(db, group_id)
        if not post:
            return {"success": False, "error": "No posts in group"}
        return await PostingService.post_single(db, account, post)
    
    @staticmethod
    async def post_bulk(db: Session, accounts: List[Account], post: Post) -> List[Dict]:
        tasks = [PostingService.post_single(db, account, post) for account in accounts]
        return await asyncio.gather(*tasks)
    
    @staticmethod
    def check_rate_limit(account: Account) -> Dict:
        decrypted_token = AccountService.get_decrypted_token(account)
        client = ThreadsAPIClient(decrypted_token)
        return client.get_publishing_limit(account.threads_user_id)
