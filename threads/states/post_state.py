import reflex as rx
from typing import List, Dict
from .base_state import BaseState
from ..services import PostGroupService, PostService
from ..models.post import MediaType

class PostState(BaseState):
    groups: List[Dict] = []
    posts: List[Dict] = []
    selected_group_id: int = 0
    show_add_group_modal: bool = False
    show_add_post_modal: bool = False
    
    # グループフォーム
    form_group_name: str = ""
    form_group_description: str = ""
    
    # 投稿フォーム
    form_post_text: str = ""
    form_media_type: str = "TEXT"
    form_media_urls: str = ""
    
    def load_groups(self):
        db = self.get_db()
        try:
            groups = PostGroupService.get_all_groups(db)
            self.groups = [
                {"id": g.id, "name": g.name, "description": g.description or ""}
                for g in groups
            ]
        finally:
            db.close()
    
    def load_posts(self, group_id: int):
        self.selected_group_id = group_id
        db = self.get_db()
        try:
            posts = PostService.get_posts_by_group(db, group_id)
            self.posts = [
                {
                    "id": p.id,
                    "text": p.text or "",
                    "media_type": p.media_type.value,
                    "media_urls": p.media_urls or [],
                }
                for p in posts
            ]
        finally:
            db.close()
    
    def add_group(self):
        if not self.form_group_name:
            return
        
        db = self.get_db()
        try:
            PostGroupService.create_group(db, self.form_group_name, self.form_group_description)
            self.form_group_name = ""
            self.form_group_description = ""
            self.show_add_group_modal = False
            self.load_groups()
        finally:
            db.close()
    
    def add_post(self):
        if not self.form_post_text or self.selected_group_id == 0:
            return
        
        db = self.get_db()
        try:
            media_urls = [url.strip() for url in self.form_media_urls.split("\n") if url.strip()] if self.form_media_urls else None
            PostService.create_post(
                db,
                group_id=self.selected_group_id,
                media_type=MediaType[self.form_media_type],
                text=self.form_post_text,
                media_urls=media_urls
            )
            self.form_post_text = ""
            self.form_media_urls = ""
            self.show_add_post_modal = False
            self.load_posts(self.selected_group_id)
        finally:
            db.close()
    
    def delete_post(self, post_id: int):
        db = self.get_db()
        try:
            PostService.delete_post(db, post_id)
            self.load_posts(self.selected_group_id)
        finally:
            db.close()
