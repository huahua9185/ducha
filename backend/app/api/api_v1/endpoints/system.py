from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User

router = APIRouter()


@router.get("/")
def read_system_config(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_system_config)
) -> Any:
    """获取系统配置"""
    # TODO: 实现系统管理逻辑
    return {"message": "系统管理功能待实现"}