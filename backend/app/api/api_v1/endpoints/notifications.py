from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.notification import NotificationType, NotificationStatus
from app.services import notification_service

router = APIRouter()


@router.get("/")
def read_notifications(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    status: NotificationStatus = Query(None, description="通知状态"),
    type: NotificationType = Query(None, description="通知类型"),
    unread_only: bool = Query(False, description="仅显示未读"),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """获取用户通知列表"""
    notifications = notification_service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
        type=type,
        unread_only=unread_only
    )
    
    total = notification_service.count_user_notifications(
        db=db,
        user_id=current_user.id,
        status=status,
        type=type,
        unread_only=unread_only
    )
    
    return {
        "items": notifications,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/stats")
def get_notification_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """获取通知统计"""
    stats = notification_service.get_notification_stats(db, current_user.id)
    return stats


@router.post("/{notification_id}/read")
def mark_notification_as_read(
    *,
    db: Session = Depends(deps.get_db),
    notification_id: UUID,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """标记通知为已读"""
    success = notification_service.mark_notification_as_read(
        db=db, notification_id=notification_id, user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    return {"message": "通知已标记为已读"}


@router.post("/read-all")
def mark_all_notifications_as_read(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """标记所有通知为已读"""
    count = notification_service.mark_all_notifications_as_read(db, current_user.id)
    return {"message": f"已标记 {count} 条通知为已读", "count": count}


@router.delete("/{notification_id}")
def delete_notification(
    *,
    db: Session = Depends(deps.get_db),
    notification_id: UUID,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """删除通知"""
    success = notification_service.delete_notification(
        db=db, notification_id=notification_id, user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    return {"message": "通知删除成功"}


@router.post("/{notification_id}/confirm")
def confirm_notification(
    *,
    db: Session = Depends(deps.get_db),
    notification_id: UUID,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """确认通知"""
    success = notification_service.confirm_notification(
        db=db, notification_id=notification_id, user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在或不需要确认"
        )
    
    return {"message": "通知确认成功"}


@router.get("/system")
def get_system_notifications(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    type: NotificationType = Query(None, description="通知类型"),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """获取系统通知"""
    notifications = notification_service.get_system_notifications(
        db=db, skip=skip, limit=limit, type=type
    )
    
    return {
        "items": notifications,
        "page": skip // limit + 1,
        "size": limit
    }


# 管理员功能
@router.post("/send-bulk")
def send_bulk_notification(
    *,
    db: Session = Depends(deps.get_db),
    title: str,
    content: str,
    type: NotificationType,
    recipient_ids: List[UUID],
    current_user: User = Depends(deps.require_system_config)
) -> Any:
    """批量发送通知"""
    from app.models.notification import NotificationChannel
    
    notifications = notification_service.send_bulk_notification(
        db=db,
        title=title,
        content=content,
        type=type,
        channels=[NotificationChannel.SYSTEM],
        recipient_ids=recipient_ids,
        sender_id=current_user.id
    )
    
    return {
        "message": f"成功发送 {len(notifications)} 条通知",
        "count": len(notifications)
    }


@router.post("/retry-failed")
def retry_failed_notifications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_system_config)
) -> Any:
    """重试发送失败的通知"""
    success_count = notification_service.retry_failed_notifications(db)
    
    return {
        "message": f"重试发送完成，成功 {success_count} 条",
        "success_count": success_count
    }


@router.post("/cleanup-expired")
def cleanup_expired_notifications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_system_config)
) -> Any:
    """清理过期通知"""
    cleanup_count = notification_service.cleanup_expired_notifications(db)
    
    return {
        "message": f"清理了 {cleanup_count} 条过期通知",
        "cleanup_count": cleanup_count
    }