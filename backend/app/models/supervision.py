from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from enum import Enum
from .base import Base


class SupervisionType(str, Enum):
    """督办类型"""
    REGULAR = "regular"        # 常规督办
    EMERGENCY = "emergency"    # 应急督办
    KEY = "key"               # 重点督办
    FOLLOW_UP = "follow_up"   # 跟踪督办


class SupervisionStatus(str, Enum):
    """督办状态"""
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待办
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"   # 已完成
    OVERDUE = "overdue"      # 逾期
    SUSPENDED = "suspended"   # 暂停
    CANCELLED = "cancelled"   # 取消


class SupervisionUrgency(str, Enum):
    """紧急程度"""
    LOW = "low"              # 一般
    MEDIUM = "medium"        # 急办
    HIGH = "high"            # 特急


class TaskStatus(str, Enum):
    """任务状态"""
    ASSIGNED = "assigned"    # 已分配
    ACCEPTED = "accepted"    # 已接收
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    REJECTED = "rejected"    # 已拒绝
    OVERDUE = "overdue"     # 逾期


class SupervisionItem(Base):
    """督办事项模型"""
    __tablename__ = "supervision_item"
    
    # 督办编号
    number: str = Column(String(50), unique=True, nullable=False, comment="督办编号")
    
    # 督办标题
    title: str = Column(String(200), nullable=False, comment="督办标题")
    
    # 督办内容
    content: str = Column(Text, nullable=False, comment="督办内容")
    
    # 督办类型
    type: SupervisionType = Column(
        SQLEnum(SupervisionType),
        nullable=False,
        default=SupervisionType.REGULAR,
        comment="督办类型"
    )
    
    # 紧急程度
    urgency: SupervisionUrgency = Column(
        SQLEnum(SupervisionUrgency),
        nullable=False,
        default=SupervisionUrgency.MEDIUM,
        comment="紧急程度"
    )
    
    # 督办状态
    status: SupervisionStatus = Column(
        SQLEnum(SupervisionStatus),
        nullable=False,
        default=SupervisionStatus.DRAFT,
        comment="督办状态"
    )
    
    # 创建人ID
    creator_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=False,
        comment="创建人ID"
    )
    
    # 责任单位ID
    responsible_department_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('department.id'),
        nullable=False,
        comment="责任单位ID"
    )
    
    # 协办单位ID列表（JSON存储）
    cooperating_departments: List[str] = Column(
        JSON,
        nullable=True,
        comment="协办单位ID列表"
    )
    
    # 督办来源
    source: str = Column(String(100), nullable=True, comment="督办来源")
    
    # 开始时间
    start_date: datetime = Column(DateTime(timezone=True), nullable=False, comment="开始时间")
    
    # 截止时间
    deadline: datetime = Column(DateTime(timezone=True), nullable=False, comment="截止时间")
    
    # 实际完成时间
    actual_completion_date: datetime = Column(DateTime(timezone=True), nullable=True, comment="实际完成时间")
    
    # 完成率
    completion_rate: int = Column(Integer, default=0, nullable=False, comment="完成率")
    
    # 预期成果
    expected_result: str = Column(Text, nullable=True, comment="预期成果")
    
    # 实际成果
    actual_result: str = Column(Text, nullable=True, comment="实际成果")
    
    # 质量评分
    quality_score: float = Column(Numeric(3, 2), nullable=True, comment="质量评分")
    
    # 效率评分
    efficiency_score: float = Column(Numeric(3, 2), nullable=True, comment="效率评分")
    
    # 满意度评分
    satisfaction_score: float = Column(Numeric(3, 2), nullable=True, comment="满意度评分")
    
    # 总体评分
    overall_score: float = Column(Numeric(3, 2), nullable=True, comment="总体评分")
    
    # 评价意见
    evaluation_comment: str = Column(Text, nullable=True, comment="评价意见")
    
    # 是否公开
    is_public: bool = Column(Boolean, default=False, nullable=False, comment="是否公开")
    
    # 是否重点督办
    is_key: bool = Column(Boolean, default=False, nullable=False, comment="是否重点督办")
    
    # 标签（JSON存储）
    tags: List[str] = Column(JSON, nullable=True, comment="标签")
    
    # 扩展数据（JSON存储）
    extra_data: dict = Column(JSON, nullable=True, comment="扩展数据")
    
    # 关系映射
    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id], back_populates="created_supervisions")
    responsible_department: Mapped["Department"] = relationship("Department", back_populates="supervision_items")
    task_assignments: Mapped[List["TaskAssignment"]] = relationship("TaskAssignment", back_populates="supervision_item", cascade="all, delete-orphan")
    progress_reports: Mapped[List["ProgressReport"]] = relationship("ProgressReport", back_populates="supervision_item", cascade="all, delete-orphan")
    status_logs: Mapped[List["StatusLog"]] = relationship("StatusLog", back_populates="supervision_item", cascade="all, delete-orphan")
    attachments: Mapped[List["Attachment"]] = relationship("Attachment", back_populates="supervision_item")
    
    def __repr__(self) -> str:
        return f"<SupervisionItem(number={self.number}, title={self.title})>"


class TaskAssignment(Base):
    """任务分配模型"""
    __tablename__ = "task_assignment"
    
    # 所属督办事项ID
    supervision_item_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('supervision_item.id'),
        nullable=False,
        comment="所属督办事项ID"
    )
    
    # 任务标题
    title: str = Column(String(200), nullable=False, comment="任务标题")
    
    # 任务描述
    description: str = Column(Text, nullable=True, comment="任务描述")
    
    # 被分配人ID
    assignee_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=False,
        comment="被分配人ID"
    )
    
    # 分配给部门ID
    assigned_department_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('department.id'),
        nullable=True,
        comment="分配给部门ID"
    )
    
    # 任务状态
    status: TaskStatus = Column(
        SQLEnum(TaskStatus),
        nullable=False,
        default=TaskStatus.ASSIGNED,
        comment="任务状态"
    )
    
    # 优先级
    priority: int = Column(Integer, default=1, nullable=False, comment="优先级")
    
    # 开始时间
    start_date: datetime = Column(DateTime(timezone=True), nullable=True, comment="开始时间")
    
    # 截止时间
    deadline: datetime = Column(DateTime(timezone=True), nullable=False, comment="截止时间")
    
    # 完成时间
    completion_date: datetime = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    
    # 完成率
    completion_rate: int = Column(Integer, default=0, nullable=False, comment="完成率")
    
    # 工作量估计（小时）
    estimated_hours: float = Column(Numeric(8, 2), nullable=True, comment="工作量估计")
    
    # 实际工作量（小时）
    actual_hours: float = Column(Numeric(8, 2), nullable=True, comment="实际工作量")
    
    # 备注
    notes: str = Column(Text, nullable=True, comment="备注")
    
    # 关系映射
    supervision_item: Mapped["SupervisionItem"] = relationship("SupervisionItem", back_populates="task_assignments")
    assignee: Mapped["User"] = relationship("User", back_populates="assigned_tasks")
    assigned_department: Mapped["Department"] = relationship("Department", back_populates="task_assignments")
    progress_reports: Mapped[List["ProgressReport"]] = relationship("ProgressReport", back_populates="task_assignment")
    
    def __repr__(self) -> str:
        return f"<TaskAssignment(title={self.title}, assignee_id={self.assignee_id})>"


class ProgressReport(Base):
    """进度报告模型"""
    __tablename__ = "progress_report"
    
    # 所属督办事项ID
    supervision_item_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('supervision_item.id'),
        nullable=False,
        comment="所属督办事项ID"
    )
    
    # 所属任务分配ID（可选）
    task_assignment_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('task_assignment.id'),
        nullable=True,
        comment="所属任务分配ID"
    )
    
    # 报告人ID
    reporter_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=False,
        comment="报告人ID"
    )
    
    # 报告标题
    title: str = Column(String(200), nullable=False, comment="报告标题")
    
    # 报告内容
    content: str = Column(Text, nullable=False, comment="报告内容")
    
    # 当前进度
    progress_rate: int = Column(Integer, default=0, nullable=False, comment="当前进度")
    
    # 已完成工作
    completed_work: str = Column(Text, nullable=True, comment="已完成工作")
    
    # 下一步计划
    next_plan: str = Column(Text, nullable=True, comment="下一步计划")
    
    # 遇到的问题
    issues: str = Column(Text, nullable=True, comment="遇到的问题")
    
    # 需要的支持
    support_needed: str = Column(Text, nullable=True, comment="需要的支持")
    
    # 预计完成时间
    estimated_completion: datetime = Column(DateTime(timezone=True), nullable=True, comment="预计完成时间")
    
    # 风险评估
    risk_assessment: str = Column(Text, nullable=True, comment="风险评估")
    
    # 报告时间
    report_date: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="报告时间"
    )
    
    # 是否重要报告
    is_important: bool = Column(Boolean, default=False, nullable=False, comment="是否重要报告")
    
    # 关系映射
    supervision_item: Mapped["SupervisionItem"] = relationship("SupervisionItem", back_populates="progress_reports")
    task_assignment: Mapped[Optional["TaskAssignment"]] = relationship("TaskAssignment", back_populates="progress_reports")
    reporter: Mapped["User"] = relationship("User", back_populates="progress_reports")
    attachments: Mapped[List["Attachment"]] = relationship("Attachment", back_populates="progress_report")
    
    def __repr__(self) -> str:
        return f"<ProgressReport(title={self.title}, reporter_id={self.reporter_id})>"


class StatusLog(Base):
    """状态变更日志模型"""
    __tablename__ = "status_log"
    
    # 所属督办事项ID
    supervision_item_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('supervision_item.id'),
        nullable=False,
        comment="所属督办事项ID"
    )
    
    # 操作人ID
    operator_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=False,
        comment="操作人ID"
    )
    
    # 操作类型
    action_type: str = Column(String(50), nullable=False, comment="操作类型")
    
    # 原状态
    old_status: str = Column(String(50), nullable=True, comment="原状态")
    
    # 新状态
    new_status: str = Column(String(50), nullable=False, comment="新状态")
    
    # 操作原因
    reason: str = Column(Text, nullable=True, comment="操作原因")
    
    # 操作时间
    action_time: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="操作时间"
    )
    
    # 额外数据
    extra_data: dict = Column(JSON, nullable=True, comment="额外数据")
    
    # 关系映射
    supervision_item: Mapped["SupervisionItem"] = relationship("SupervisionItem", back_populates="status_logs")
    operator: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        return f"<StatusLog(action_type={self.action_type}, operator_id={self.operator_id})>"