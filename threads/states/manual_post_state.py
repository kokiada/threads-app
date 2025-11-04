import reflex as rx
import asyncio
from typing import List
from ..models.post import MediaType
from ..services.account_service import AccountService
from ..services.post_group_service import PostGroupService
from ..services.post_service import PostService
from ..services.posting_service import PostingService

from .base_state import BaseState

class ManualPostState(BaseState):
    accounts: List[dict] = []
    groups: List[dict] = []
    posts: List[dict] = []
    selected_account_ids: List[int] = []
    selected_group_id: int = 0
    selected_post_id: int = 0
    post_text: str = ""
    media_type: str = "TEXT"
    media_urls: str = ""
    uploaded_files: List[str] = []
    uploading: bool = False
    posting: bool = False
    result_message: str = ""
    
    def load_accounts(self):
        with self.get_db() as db:
            accounts = AccountService.get_all_accounts(db)
            self.accounts = [
                {"id": a.id, "name": a.name, "status": a.status.value}
                for a in accounts if a.status.value == "active"
            ]
    
    def load_groups(self):
        with self.get_db() as db:
            groups = PostGroupService.get_all_groups(db)
            self.groups = [{"id": g.id, "name": g.name} for g in groups]
    
    def load_posts(self):
        if not self.selected_group_id:
            return
        with self.get_db() as db:
            posts = PostService.get_posts_by_group(db, self.selected_group_id)
            self.posts = [
                {"id": p.id, "text": p.text[:50], "media_type": p.media_type.value}
                for p in posts
            ]
    
    def set_selected_group_id(self, value: str):
        self.selected_group_id = int(value)
        self.load_posts()
    
    def set_selected_post_id(self, value: str):
        self.selected_post_id = int(value)
    
    def set_post_text(self, value: str):
        self.post_text = value
    
    def set_media_type(self, value: str):
        self.media_type = value
    
    def set_media_urls(self, value: str):
        self.media_urls = value
    
    async def handle_upload(self, files: List[rx.UploadFile]):
        import logging
        import os
        logger = logging.getLogger(__name__)
        
        self.uploading = True
        self.uploaded_files = []
        
        upload_dir = "uploaded_files"
        os.makedirs(upload_dir, exist_ok=True)
        
        for file in files:
            try:
                upload_data = await file.read()
                file_path = os.path.join(upload_dir, file.filename)
                
                with open(file_path, "wb") as f:
                    f.write(upload_data)
                
                # 公開URLを生成（BASE_URLを使用）
                base_url = os.getenv("BASE_URL", "http://localhost:3000")
                public_url = f"{base_url}/{file_path}"
                self.uploaded_files.append(public_url)
                logger.info(f"File uploaded: {public_url}")
            except Exception as e:
                logger.error(f"Upload error: {str(e)}")
        
        self.media_urls = ",".join(self.uploaded_files)
        self.uploading = False
        self.result_message = f"{len(self.uploaded_files)}件のファイルをアップロードしました"
    
    def set_account_selection(self, account_id: int, checked: bool):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"set_account_selection: account_id={account_id}, checked={checked}")
        
        if checked and account_id not in self.selected_account_ids:
            self.selected_account_ids.append(account_id)
            logger.info(f"Added account {account_id}. Current: {self.selected_account_ids}")
        elif not checked and account_id in self.selected_account_ids:
            self.selected_account_ids.remove(account_id)
            logger.info(f"Removed account {account_id}. Current: {self.selected_account_ids}")
    
    async def post_manual(self):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"post_manual called: selected_account_ids={self.selected_account_ids}, post_text={self.post_text[:50] if self.post_text else 'empty'}")
        
        if not self.selected_account_ids or not self.post_text:
            self.result_message = "アカウントと投稿内容を選択してください"
            return
        
        self.posting = True
        self.result_message = ""
        yield
        
        try:
            with self.get_db() as db:
                accounts = [AccountService.get_account(db, aid) for aid in self.selected_account_ids]
                logger.info(f"投稿対象アカウント: {[a.name for a in accounts]}")
                
                media_type = MediaType[self.media_type]
                urls = [u.strip() for u in self.media_urls.split(",") if u.strip()] if self.media_urls else None
                
                from ..models.post import Post
                temp_post = Post(
                    group_id=1,
                    media_type=media_type,
                    text=self.post_text,
                    media_urls=urls
                )
                logger.info(f"投稿内容: {self.post_text[:50]}...")
                
                results = await PostingService.post_bulk(db, accounts, temp_post)
                logger.info(f"投稿結果: {results}")
                
                success_count = sum(1 for r in results if r.get("success"))
                failed_results = [r for r in results if not r.get("success")]
                
                if failed_results:
                    errors = ", ".join([r.get("error", "Unknown") for r in failed_results])
                    self.result_message = f"投稿完了: {success_count}/{len(accounts)}件成功. エラー: {errors}"
                else:
                    self.result_message = f"投稿完了: {success_count}/{len(accounts)}件成功"
        except Exception as e:
            logger.error(f"投稿エラー: {str(e)}", exc_info=True)
            self.result_message = f"エラー: {str(e)}"
        finally:
            self.posting = False
    
    async def post_from_template(self):
        if not self.selected_account_ids or not self.selected_post_id:
            self.result_message = "アカウントと投稿テンプレートを選択してください"
            return
        
        self.posting = True
        self.result_message = ""
        yield
        
        with self.get_db() as db:
            accounts = [AccountService.get_account(db, aid) for aid in self.selected_account_ids]
            post = PostService.get_post(db, self.selected_post_id)
            
            if not post:
                self.result_message = "投稿が見つかりません"
                self.posting = False
                return
            
            results = await PostingService.post_bulk(db, accounts, post)
            success_count = sum(1 for r in results if r.get("success"))
            self.result_message = f"投稿完了: {success_count}/{len(accounts)}件成功"
        
        self.posting = False
