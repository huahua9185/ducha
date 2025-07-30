from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class NotificationBase(BaseModel):
    """通知基础模型"""
    title: str
    content: str
    type: str = "info"
    is_read: bool = False


class NotificationCreate(NotificationBase):
    """创建通知请求"""
    recipient_id: UUID
    sender_id: Optional[UUID] = None


class NotificationUpdate(BaseModel):
    """更新通知请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    """通知响应"""
    id: UUID
    recipient_id: UUID
    sender_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True