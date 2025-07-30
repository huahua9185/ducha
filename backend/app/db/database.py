from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables():
    """创建数据库表"""
    from app.db.base import Base
    from app.db.session import engine
    Base.metadata.create_all(bind=engine)