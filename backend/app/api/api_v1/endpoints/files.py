from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User

router = APIRouter()


@router.get("/")
def read_files(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """获取文件列表"""
    # TODO: 实现文件管理逻辑
    return {"message": "文件管理功能待实现"}