from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.security import verify_password as verify_pwd, get_password_hash
from app.models.user import User
from app.services.user_service import get_user_by_username


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """用户认证"""
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_pwd(password, user.password_hash):
        return None
    return user


def update_last_login(db: Session, user_id: UUID, client_ip: str = None) -> User:
    """更新最后登录时间"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.last_login_at = datetime.utcnow()
        if client_ip:
            user.last_login_ip = client_ip
        db.commit()
        db.refresh(user)
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return verify_pwd(plain_password, hashed_password)