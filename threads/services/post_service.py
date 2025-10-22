from sqlalchemy.orm import Session
from typing import List, Optional
import random
from ..models.post import Post, MediaType
from ..utils.validators import validate_post_text

class PostService:
    @staticmethod
    def create_post(db: Session, group_id: int, media_type: MediaType, 
                   text: Optional[str] = None, media_urls: Optional[List[str]] = None) -> Post:
        if text:
            validate_post_text(text)
        
        post = Post(
            group_id=group_id,
            media_type=media_type,
            text=text,
            media_urls=media_urls
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return post
    
    @staticmethod
    def get_post(db: Session, post_id: int) -> Optional[Post]:
        return db.query(Post).filter(Post.id == post_id).first()
    
    @staticmethod
    def get_posts_by_group(db: Session, group_id: int) -> List[Post]:
        return db.query(Post).filter(Post.group_id == group_id).all()
    
    @staticmethod
    def update_post(db: Session, post_id: int, text: Optional[str] = None, 
                   media_urls: Optional[List[str]] = None) -> Optional[Post]:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            return None
        
        if text is not None:
            validate_post_text(text)
            post.text = text
        if media_urls is not None:
            post.media_urls = media_urls
        
        db.commit()
        db.refresh(post)
        return post
    
    @staticmethod
    def delete_post(db: Session, post_id: int) -> bool:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            return False
        db.delete(post)
        db.commit()
        return True
    
    @staticmethod
    def get_random_post_from_group(db: Session, group_id: int) -> Optional[Post]:
        posts = db.query(Post).filter(Post.group_id == group_id).all()
        return random.choice(posts) if posts else None
