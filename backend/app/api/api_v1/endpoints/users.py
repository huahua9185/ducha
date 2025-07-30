from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.user import User, UserCreate, UserUpdate, UserList, UserRoleAssign
from app.services import user_service
from app.models.user import User as UserModel

router = APIRouter()


@router.get("/", response_model=UserList)
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    search: str = Query(None, description="搜索关键词"),
    department_id: UUID = Query(None, description="部门ID"),
    is_active: bool = Query(None, description="是否激活"),
    current_user: UserModel = Depends(deps.require_user_manage)
) -> Any:
    """获取用户列表"""
    users = user_service.get_users(
        db, skip=skip, limit=limit, search=search, 
        department_id=department_id, is_active=is_active
    )
    total = user_service.count_users(
        db, search=search, department_id=department_id, is_active=is_active
    )
    
    return {
        "items": users,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: UserModel = Depends(deps.require_user_manage)
) -> Any:
    """创建用户"""
    # 检查用户名是否存在
    if user_service.check_username_exists(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否存在
    if user_in.email and user_service.check_email_exists(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被使用"
        )
    
    user = user_service.create_user(db, user_create=user_in)
    return user


@router.get("/{user_id}", response_model=User)
def read_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """获取用户详情"""
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 只有管理员或用户本人可以查看详情
    if not current_user.is_superuser and current_user.id != user_id:
        # 检查是否有管理权限
        user_permissions = user_service.get_user_permissions(db, user_id=current_user.id)
        if "user:read" not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    
    return user


@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    user_in: UserUpdate,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """更新用户"""
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 权限检查
    if not current_user.is_superuser and current_user.id != user_id:
        user_permissions = user_service.get_user_permissions(db, user_id=current_user.id)
        if "user:update" not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    
    # 检查邮箱是否被其他用户使用
    if user_in.email and user_service.check_email_exists(db, user_in.email, exclude_user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被其他用户使用"
        )
    
    user = user_service.update_user(db, user_id=user_id, user_update=user_in)
    return user


@router.delete("/{user_id}")
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    current_user: UserModel = Depends(deps.require_user_manage)
) -> Any:
    """删除用户"""
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    success = user_service.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="删除失败"
        )
    
    return {"message": "用户删除成功"}


@router.post("/{user_id}/activate")
def activate_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    current_user: UserModel = Depends(deps.require_user_manage)
) -> Any:
    """激活用户"""
    user = user_service.activate_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {"message": "用户激活成功"}


@router.post("/{user_id}/deactivate")
def deactivate_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    current_user: UserModel = Depends(deps.require_user_manage)
) -> Any:
    """停用用户"""
    user = user_service.deactivate_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能停用自己
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能停用自己"
        )
    
    return {"message": "用户停用成功"}


@router.post("/{user_id}/roles", response_model=User)
def assign_user_roles(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    role_assign: UserRoleAssign,
    current_user: UserModel = Depends(deps.require_role_manage)
) -> Any:
    """分配用户角色"""
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    success = user_service.assign_roles(db, user_id=user_id, role_ids=role_assign.role_ids)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色分配失败"
        )
    
    return user


@router.get("/{user_id}/subordinates", response_model=List[User])
def get_user_subordinates(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """获取用户下属"""
    # 只能查看自己的下属或有管理权限
    if not current_user.is_superuser and current_user.id != user_id:
        user_permissions = user_service.get_user_permissions(db, user_id=current_user.id)
        if "user:read" not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    
    subordinates = user_service.get_subordinates(db, user_id=user_id)
    return subordinates