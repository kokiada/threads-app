import reflex as rx
import asyncio
from typing import List
from ..models.post import MediaType
from ..services.account_service import AccountService
from ..services.post_group_service import PostGroupService
from ..services.post_service import PostService
from ..services.posting_service import PostingService
from ..utils.cloudinary_uploader import upload_file
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
        """ファイルをCloudinaryにアップロード"""
        self.uploading = True
        self.uploaded_files = []
        
        for file in files:
            # ファイルを一時保存
            upload_data = await file.read()
            temp_path = f"/tmp/{file.filename}"
            
            with open(temp_path, "wb") as f:
                f.write(upload_data)
            
            # Cloudinaryにアップロード
            resource_type = "video" if self.media_type == "VIDEO" else "image"
            url = upload_file(temp_path, resource_type)
            
            if url:
                self.uploaded_files.append(url)
        
        # アップロードされたURLをmedia_urlsに設定
        self.media_urls = ",".join(self.uploaded_files)
        self.uploading = False
        self.result_message = f"{len(self.uploaded_files)}件のファイルをアップロードしました"
    
    def toggle_account(self, account_id: int):
        def handler(checked: bool):
            if checked and account_id not in self.selected_account_ids:
                self.selected_account_ids.append(account_id)
            elif not checked and account_id in self.selected_account_ids:
                self.selected_account_ids.remove(account_id)
        return handler
    
    async def post_manual(self):
        import logging
        logger = logging.getLogger(__name__)
        
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
