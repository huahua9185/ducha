from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import relationship, Mapped
from enum import Enum
from .base import Base


class NotificationType(str, Enum):
    """通知类型"""
    SYSTEM = "system"         # 系统通知
    TASK = "task"            # 任务通知
    REMINDER = "reminder"     # 提醒通知
    WARNING = "warning"       # 警告通知
    APPROVAL = "approval"     # 审批通知


class NotificationStatus(str, Enum):
    """通知状态"""
    PENDING = "pending"       # 待发送
    SENT = "sent"            # 已发送
    READ = "read"            # 已读
    FAILED = "failed"        # 发送失败


class NotificationChannel(str, Enum):
    """通知渠道"""
    SYSTEM = "system"         # 系统内通知
    EMAIL = "email"          # 邮件
    SMS = "sms"              # 短信
    WECHAT = "wechat"        # 微信
    PUSH = "push"            # 推送


class Notification(Base):
    """通知模型"""
    __tablename__ = "notification"
    
    # 通知标题
    title: str = Column(String(200), nullable=False, comment="通知标题")
    
    # 通知内容
    content: str = Column(Text, nullable=False, comment="通知内容")
    
    # 通知类型
    type: NotificationType = Column(
        SQLEnum(NotificationType),
        nullable=False,
        default=NotificationType.SYSTEM,
        comment="通知类型"
    )
    
    # 通知状态
    status: NotificationStatus = Column(
        SQLEnum(NotificationStatus),
        nullable=False,
        default=NotificationStatus.PENDING,
        comment="通知状态"
    )
    
    # 通知渠道
    channels: List[str] = Column(JSON, nullable=False, comment="通知渠道")
    
    # 发送者ID
    sender_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=True,
        comment="发送者ID"
    )
    
    # 接收者ID
    recipient_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=False,
        comment="接收者ID"
    )
    
    # 关联业务ID
    related_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        nullable=True,
        comment="关联业务ID"
    )
    
    # 关联业务类型
    related_type: str = Column(String(50), nullable=True, comment="关联业务类型")
    
    # 优先级
    priority: int = Column(Integer, default=1, nullable=False, comment="优先级")
    
    # 是否需要确认
    require_confirm: bool = Column(Boolean, default=False, nullable=False, comment="是否需要确认")
    
    # 确认时间
    confirmed_at: datetime = Column(DateTime(timezone=True), nullable=True, comment="确认时间")
    
    # 预定发送时间
    scheduled_at: datetime = Column(DateTime(timezone=True), nullable=True, comment="预定发送时间")
    
    # 实际发送时间
    sent_at: datetime = Column(DateTime(timezone=True), nullable=True, comment="实际发送时间")
    
    # 阅读时间
    read_at: datetime = Column(DateTime(timezone=True), nullable=True, comment="阅读时间")
    
    # 过期时间
    expires_at: datetime = Column(DateTime(timezone=True), nullable=True, comment="过期时间")
    
    # 重试次数
    retry_count: int = Column(Integer, default=0, nullable=False, comment="重试次数")
    
    # 错误信息
    error_message: str = Column(Text, nullable=True, comment="错误信息")
    
    # 扩展数据
    extra_data: Dict[str, Any] = Column(JSON, nullable=True, comment="扩展数据")
    
    # 关系映射
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id])
    recipient: Mapped["User"] = relationship("User", foreign_keys=[recipient_id])
    
    def __repr__(self) -> str:
        return f"<Notification(title={self.title}, recipient_id={self.recipient_id})>"


class NotificationTemplate(Base):
    """通知模板模型"""
    __tablename__ = "notification_template"
    
    # 模板名称
    name: str = Column(String(100), nullable=False, comment="模板名称")
    
    # 模板代码
    code: str = Column(String(50), unique=True, nullable=False, comment="模板代码")
    
    # 模板描述
    description: str = Column(Text, nullable=True, comment="模板描述")
    
    # 通知类型
    type: NotificationType = Column(
        SQLEnum(NotificationType),
        nullable=False,
        comment="通知类型"
    )
    
    # 支持的渠道
    supported_channels: List[str] = Column(JSON, nullable=False, comment="支持的渠道")
    
    # 标题模板
    title_template: str = Column(String(200), nullable=False, comment="标题模板")
    
    # 内容模板
    content_template: str = Column(Text, nullable=False, comment="内容模板")
    
    # 邮件模板（HTML）
    email_template: str = Column(Text, nullable=True, comment="邮件模板")
    
    # 短信模板
    sms_template: str = Column(String(500), nullable=True, comment="短信模板")
    
    # 微信模板
    wechat_template: str = Column(Text, nullable=True, comment="微信模板")
    
    # 是否启用
    is_enabled: bool = Column(Boolean, default=True, nullable=False, comment="是否启用")
    
    # 是否系统内置
    is_builtin: bool = Column(Boolean, default=False, nullable=False, comment="是否系统内置")
    
    # 变量说明（JSON）
    variables: Dict[str, str] = Column(JSON, nullable=True, comment="变量说明")
    
    # 排序
    sort_order: int = Column(Integer, default=0, nullable=False, comment="排序")
    
    def __repr__(self) -> str:
        return f"<NotificationTemplate(name={self.name}, code={self.code})>"


class NotificationRule(Base):
    """通知规则模型"""
    __tablename__ = "notification_rule"
    
    # 规则名称
    name: str = Column(String(100), nullable=False, comment="规则名称")
    
    # 规则描述
    description: str = Column(Text, nullable=True, comment="规则描述")
    
    # 事件类型
    event_type: str = Column(String(50), nullable=False, comment="事件类型")
    
    # 触发条件（JSON）
    trigger_conditions: Dict[str, Any] = Column(JSON, nullable=False, comment="触发条件")
    
    # 通知模板ID
    template_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('notification_template.id'),
        nullable=False,
        comment="通知模板ID"
    )
    
    # 接收者规则（JSON）
    recipient_rules: Dict[str, Any] = Column(JSON, nullable=False, comment="接收者规则")
    
    # 通知渠道
    channels: List[str] = Column(JSON, nullable=False, comment="通知渠道")
    
    # 延迟发送（分钟）
    delay_minutes: int = Column(Integer, default=0, nullable=False, comment="延迟发送")
    
    # 是否启用
    is_enabled: bool = Column(Boolean, default=True, nullable=False, comment="是否启用")
    
    # 优先级
    priority: int = Column(Integer, default=1, nullable=False, comment="优先级")
    
    # 关系映射
    template: Mapped["NotificationTemplate"] = relationship("NotificationTemplate")
    
    def __repr__(self) -> str:
        return f"<NotificationRule(name={self.name}, event_type={self.event_type})>"