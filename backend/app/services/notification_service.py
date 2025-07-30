from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.notification import (
    Notification, NotificationTemplate, NotificationRule,
    NotificationType, NotificationStatus, NotificationChannel
)
from app.models.user import User
from app.schemas.notification import NotificationCreate


def create_notification(
    db: Session,
    title: str,
    content: str,
    type: NotificationType,
    channels: List[NotificationChannel],
    recipient_id: UUID,
    sender_id: UUID = None,
    related_id: UUID = None,
    related_type: str = None,
    priority: int = 1,
    require_confirm: bool = False,
    scheduled_at: datetime = None,
    expires_at: datetime = None
) -> Notification:
    """创建通知"""
    db_notification = Notification(
        title=title,
        content=content,
        type=type,
        status=NotificationStatus.PENDING,
        channels=channels,
        sender_id=sender_id,
        recipient_id=recipient_id,
        related_id=related_id,
        related_type=related_type,
        priority=priority,
        require_confirm=require_confirm,
        scheduled_at=scheduled_at or datetime.utcnow(),
        expires_at=expires_at,
        retry_count=0,
        created_by=sender_id
    )
    
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    
    # 立即发送通知（如果没有设置延迟）
    if not scheduled_at or scheduled_at <= datetime.utcnow():
        send_notification(db, db_notification.id)
    
    return db_notification


def send_notification(db: Session, notification_id: UUID) -> bool:
    """发送通知"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        return False
    
    try:
        # 标记为已发送
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()
        
        # 根据不同渠道发送通知
        for channel in notification.channels:
            if channel == NotificationChannel.SYSTEM:
                # 系统内通知，无需额外处理
                pass
            elif channel == NotificationChannel.EMAIL:
                # 发送邮件通知
                send_email_notification(notification)
            elif channel == NotificationChannel.SMS:
                # 发送短信通知
                send_sms_notification(notification)
            elif channel == NotificationChannel.WECHAT:
                # 发送微信通知
                send_wechat_notification(notification)
        
        db.commit()
        return True
        
    except Exception as e:
        # 发送失败，记录错误信息
        notification.status = NotificationStatus.FAILED
        notification.error_message = str(e)
        notification.retry_count += 1
        db.commit()
        return False


def send_email_notification(notification: Notification):
    """发送邮件通知"""
    # TODO: 实现邮件发送逻辑
    # 这里可以集成邮件服务提供商的API
    pass


def send_sms_notification(notification: Notification):
    """发送短信通知"""
    # TODO: 实现短信发送逻辑
    # 这里可以集成短信服务提供商的API
    pass


def send_wechat_notification(notification: Notification):
    """发送微信通知"""
    # TODO: 实现微信通知发送逻辑
    # 这里可以集成企业微信或微信公众号API
    pass


def get_user_notifications(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 20,
    status: NotificationStatus = None,
    type: NotificationType = None,
    unread_only: bool = False
) -> List[Notification]:
    """获取用户通知列表"""
    query = db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.is_deleted == False
    )
    
    if status:
        query = query.filter(Notification.status == status)
    
    if type:
        query = query.filter(Notification.type == type)
    
    if unread_only:
        query = query.filter(Notification.read_at.is_(None))
    
    # 检查过期时间
    now = datetime.utcnow()
    query = query.filter(
        or_(
            Notification.expires_at.is_(None),
            Notification.expires_at > now
        )
    )
    
    return query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()


def count_user_notifications(
    db: Session,
    user_id: UUID,
    status: NotificationStatus = None,
    type: NotificationType = None,
    unread_only: bool = False
) -> int:
    """统计用户通知数量"""
    query = db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.is_deleted == False
    )
    
    if status:
        query = query.filter(Notification.status == status)
    
    if type:
        query = query.filter(Notification.type == type)
    
    if unread_only:
        query = query.filter(Notification.read_at.is_(None))
    
    # 检查过期时间
    now = datetime.utcnow()
    query = query.filter(
        or_(
            Notification.expires_at.is_(None),
            Notification.expires_at > now
        )
    )
    
    return query.count()


def mark_notification_as_read(db: Session, notification_id: UUID, user_id: UUID) -> bool:
    """标记通知为已读"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == user_id
    ).first()
    
    if not notification:
        return False
    
    notification.read_at = datetime.utcnow()
    db.commit()
    
    return True


def mark_all_notifications_as_read(db: Session, user_id: UUID) -> int:
    """标记所有通知为已读"""
    count = db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.read_at.is_(None),
        Notification.is_deleted == False
    ).update({
        Notification.read_at: datetime.utcnow()
    })
    
    db.commit()
    return count


def delete_notification(db: Session, notification_id: UUID, user_id: UUID) -> bool:
    """删除通知"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == user_id
    ).first()
    
    if not notification:
        return False
    
    notification.is_deleted = True
    notification.deleted_at = datetime.utcnow()
    db.commit()
    
    return True


def confirm_notification(db: Session, notification_id: UUID, user_id: UUID) -> bool:
    """确认通知"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == user_id,
        Notification.require_confirm == True
    ).first()
    
    if not notification:
        return False
    
    notification.confirmed_at = datetime.utcnow()
    db.commit()
    
    return True


def get_notification_stats(db: Session, user_id: UUID) -> Dict[str, int]:
    """获取通知统计"""
    now = datetime.utcnow()
    
    total_count = db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.is_deleted == False,
        or_(
            Notification.expires_at.is_(None),
            Notification.expires_at > now
        )
    ).count()
    
    unread_count = db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.read_at.is_(None),
        Notification.is_deleted == False,
        or_(
            Notification.expires_at.is_(None),
            Notification.expires_at > now
        )
    ).count()
    
    pending_confirm_count = db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.require_confirm == True,
        Notification.confirmed_at.is_(None),
        Notification.is_deleted == False,
        or_(
            Notification.expires_at.is_(None),
            Notification.expires_at > now
        )
    ).count()
    
    return {
        "total_count": total_count,
        "unread_count": unread_count,
        "pending_confirm_count": pending_confirm_count
    }


def send_bulk_notification(
    db: Session,
    title: str,
    content: str,
    type: NotificationType,
    channels: List[NotificationChannel],
    recipient_ids: List[UUID],
    sender_id: UUID = None,
    related_id: UUID = None,
    related_type: str = None
) -> List[Notification]:
    """批量发送通知"""
    notifications = []
    
    for recipient_id in recipient_ids:
        notification = create_notification(
            db=db,
            title=title,
            content=content,
            type=type,
            channels=channels,
            recipient_id=recipient_id,
            sender_id=sender_id,
            related_id=related_id,
            related_type=related_type
        )
        notifications.append(notification)
    
    return notifications


def retry_failed_notifications(db: Session, max_retries: int = 3) -> int:
    """重试发送失败的通知"""
    failed_notifications = db.query(Notification).filter(
        Notification.status == NotificationStatus.FAILED,
        Notification.retry_count < max_retries,
        Notification.is_deleted == False
    ).all()
    
    success_count = 0
    for notification in failed_notifications:
        if send_notification(db, notification.id):
            success_count += 1
    
    return success_count


def cleanup_expired_notifications(db: Session) -> int:
    """清理过期通知"""
    now = datetime.utcnow()
    
    count = db.query(Notification).filter(
        Notification.expires_at < now,
        Notification.is_deleted == False
    ).update({
        Notification.is_deleted: True,
        Notification.deleted_at: now
    })
    
    db.commit()
    return count


def get_system_notifications(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    type: NotificationType = None
) -> List[Notification]:
    """获取系统通知"""
    query = db.query(Notification).filter(
        Notification.sender_id.is_(None),  # 系统通知
        Notification.is_deleted == False
    )
    
    if type:
        query = query.filter(Notification.type == type)
    
    return query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()


# 通知模板管理
def get_notification_template(db: Session, template_code: str) -> Optional[NotificationTemplate]:
    """根据代码获取通知模板"""
    return db.query(NotificationTemplate).filter(
        NotificationTemplate.code == template_code,
        NotificationTemplate.is_enabled == True,
        NotificationTemplate.is_deleted == False
    ).first()


def render_notification_template(
    template: NotificationTemplate,
    variables: Dict[str, Any]
) -> Dict[str, str]:
    """渲染通知模板"""
    # 简单的模板变量替换
    title = template.title_template
    content = template.content_template
    
    for key, value in variables.items():
        placeholder = f"{{{key}}}"
        title = title.replace(placeholder, str(value))
        content = content.replace(placeholder, str(value))
    
    return {
        "title": title,
        "content": content
    }


def create_notification_from_template(
    db: Session,
    template_code: str,
    variables: Dict[str, Any],
    recipient_id: UUID,
    sender_id: UUID = None,
    related_id: UUID = None,
    related_type: str = None
) -> Optional[Notification]:
    """基于模板创建通知"""
    template = get_notification_template(db, template_code)
    if not template:
        return None
    
    rendered = render_notification_template(template, variables)
    
    return create_notification(
        db=db,
        title=rendered["title"],
        content=rendered["content"],
        type=template.type,
        channels=template.supported_channels,
        recipient_id=recipient_id,
        sender_id=sender_id,
        related_id=related_id,
        related_type=related_type
    )