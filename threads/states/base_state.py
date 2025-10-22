import reflex as rx
from sqlalchemy.orm import Session
from ..models.base import SessionLocal

class BaseState(rx.State):
    """全Stateの基底クラス"""
    
    def get_db(self) -> Session:
        return SessionLocal()
