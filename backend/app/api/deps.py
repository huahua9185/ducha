from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_token
from app.db.database import get_db
from app.models.user import User
from app.services import user_service


# OAuth2 认证方案
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = verify_token(token, token_type="access")
    if user_id is None:
        raise credentials_exception
    
    user = user_service.get_user(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账号已被禁用"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账号已被禁用"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前超级用户"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return current_user


def check_permission(permission: str):
    """检查权限装饰器"""
    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if current_user.is_superuser:
            return current_user
        
        # 检查用户是否有指定权限
        user_permissions = user_service.get_user_permissions(db, user_id=current_user.id)
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {permission}"
            )
        
        return current_user
    
    return permission_checker


def check_role(role: str):
    """检查角色装饰器"""
    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if current_user.is_superuser:
            return current_user
        
        # 检查用户是否有指定角色
        user_roles = user_service.get_user_roles(db, user_id=current_user.id)
        role_codes = [r.code for r in user_roles]
        if role not in role_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少角色: {role}"
            )
        
        return current_user
    
    return role_checker


def get_optional_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """获取可选的当前用户（允许匿名访问）"""
    if not token:
        return None
    
    try:
        user_id = verify_token(token, token_type="access")
        if user_id is None:
            return None
        
        user = user_service.get_user(db, user_id=user_id)
        if user is None or not user.is_active:
            return None
        
        return user
    except Exception:
        return None


class PermissionChecker:
    """权限检查器类"""
    
    def __init__(self, permission: str):
        self.permission = permission
    
    def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if current_user.is_superuser:
            return current_user
        
        user_permissions = user_service.get_user_permissions(db, user_id=current_user.id)
        if self.permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {self.permission}"
            )
        
        return current_user


class RoleChecker:
    """角色检查器类"""
    
    def __init__(self, role: str):
        self.role = role
    
    def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if current_user.is_superuser:
            return current_user
        
        user_roles = user_service.get_user_roles(db, user_id=current_user.id)
        role_codes = [r.code for r in user_roles]
        if self.role not in role_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少角色: {self.role}"
            )
        
        return current_user


# 常用权限检查器实例
require_admin = RoleChecker("admin")
require_supervisor = RoleChecker("supervisor")
require_manager = RoleChecker("manager")

# 督办相关权限
require_supervision_create = PermissionChecker("supervision:create")
require_supervision_read = PermissionChecker("supervision:read")
require_supervision_update = PermissionChecker("supervision:update")
require_supervision_delete = PermissionChecker("supervision:delete")

# 用户管理权限
require_user_manage = PermissionChecker("user:manage")
require_role_manage = PermissionChecker("role:manage")
require_department_manage = PermissionChecker("department:manage")

# 系统管理权限
require_system_config = PermissionChecker("system:config")
require_system_log = PermissionChecker("system:log")