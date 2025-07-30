from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.user import Role, RoleCreate, RoleUpdate, RoleList
from app.services import user_service
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=RoleList)
def read_roles(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(deps.require_role_manage)
) -> Any:
    """获取角色列表"""
    roles = user_service.get_roles(db, skip=skip, limit=limit)
    total = user_service.count_roles(db)
    
    return {
        "items": roles,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/{role_id}", response_model=Role)
def read_role(
    *,
    db: Session = Depends(deps.get_db),
    role_id: UUID,
    current_user: User = Depends(deps.require_role_manage)
) -> Any:
    """获取角色详情"""
    role = user_service.get_role(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return role