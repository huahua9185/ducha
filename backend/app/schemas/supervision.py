from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum

from app.schemas.user import User


class SupervisionType(str, Enum):
    """督办类型"""
    REGULAR = "regular"        # 常规督办
    EMERGENCY = "emergency"    # 应急督办
    KEY = "key"               # 重点督办
    FOLLOW_UP = "follow_up"   # 跟踪督办


class SupervisionUrgency(str, Enum):
    """紧急程度"""
    LOW = "low"              # 一般
    MEDIUM = "medium"        # 急办
    HIGH = "high"            # 特急


class SupervisionStatus(str, Enum):
    """督办状态"""
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待办
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"   # 已完成
    OVERDUE = "overdue"      # 逾期
    SUSPENDED = "suspended"   # 暂停
    CANCELLED = "cancelled"   # 取消


class TaskStatus(str, Enum):
    """任务状态"""
    ASSIGNED = "assigned"    # 已分配
    ACCEPTED = "accepted"    # 已接收
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    REJECTED = "rejected"    # 已拒绝
    OVERDUE = "overdue"     # 逾期


# 督办事项基础模式
class SupervisionItemBase(BaseModel):
    """督办事项基础模式"""
    title: str = Field(..., min_length=1, max_length=200, description="督办标题")
    content: str = Field(..., min_length=1, description="督办内容")
    type: SupervisionType = Field(SupervisionType.REGULAR, description="督办类型")
    urgency: SupervisionUrgency = Field(SupervisionUrgency.MEDIUM, description="紧急程度")
    responsible_department_id: UUID = Field(..., description="责任单位ID")
    cooperating_departments: Optional[List[UUID]] = Field(None, description="协办单位ID列表")
    source: Optional[str] = Field(None, max_length=100, description="督办来源")
    start_date: datetime = Field(..., description="开始时间")
    deadline: datetime = Field(..., description="截止时间")
    expected_result: Optional[str] = Field(None, description="预期成果")
    is_public: bool = Field(False, description="是否公开")
    is_key: bool = Field(False, description="是否重点督办")
    tags: Optional[List[str]] = Field(None, description="标签")


class SupervisionItemCreate(SupervisionItemBase):
    """创建督办事项"""
    pass


class SupervisionItemUpdate(BaseModel):
    """更新督办事项"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    type: Optional[SupervisionType] = None
    urgency: Optional[SupervisionUrgency] = None
    responsible_department_id: Optional[UUID] = None
    cooperating_departments: Optional[List[UUID]] = None
    source: Optional[str] = Field(None, max_length=100)
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    is_public: Optional[bool] = None
    is_key: Optional[bool] = None
    tags: Optional[List[str]] = None
    status: Optional[SupervisionStatus] = None


class SupervisionItem(SupervisionItemBase):
    """督办事项响应"""
    id: UUID
    number: str
    status: SupervisionStatus
    creator_id: UUID
    completion_rate: int
    actual_completion_date: Optional[datetime]
    actual_result: Optional[str]
    quality_score: Optional[float]
    efficiency_score: Optional[float]
    satisfaction_score: Optional[float]
    overall_score: Optional[float]
    evaluation_comment: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SupervisionItemDetail(SupervisionItem):
    """督办事项详情"""
    creator: User
    task_assignments: List["TaskAssignment"] = []
    progress_reports: List["ProgressReport"] = []
    status_logs: List["StatusLog"] = []


class SupervisionItemList(BaseModel):
    """督办事项列表响应"""
    items: List[SupervisionItem]
    total: int
    page: int
    size: int
    pages: int


# 任务分配相关模式
class TaskAssignmentBase(BaseModel):
    """任务分配基础模式"""
    title: str = Field(..., min_length=1, max_length=200, description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    assignee_id: UUID = Field(..., description="被分配人ID")
    assigned_department_id: Optional[UUID] = Field(None, description="分配给部门ID")
    priority: int = Field(1, ge=1, le=5, description="优先级")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    deadline: datetime = Field(..., description="截止时间")
    estimated_hours: Optional[float] = Field(None, ge=0, description="工作量估计")
    notes: Optional[str] = Field(None, description="备注")


class TaskAssignmentCreate(TaskAssignmentBase):
    """创建任务分配"""
    supervision_item_id: UUID = Field(..., description="所属督办事项ID")


class TaskAssignmentUpdate(BaseModel):
    """更新任务分配"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    assignee_id: Optional[UUID] = None
    assigned_department_id: Optional[UUID] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    completion_rate: Optional[int] = Field(None, ge=0, le=100)
    estimated_hours: Optional[float] = Field(None, ge=0)
    actual_hours: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskAssignment(TaskAssignmentBase):
    """任务分配响应"""
    id: UUID
    supervision_item_id: UUID
    status: TaskStatus
    completion_date: Optional[datetime]
    completion_rate: int
    actual_hours: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskAssignmentDetail(TaskAssignment):
    """任务分配详情"""
    assignee: User
    progress_reports: List["ProgressReport"] = []


# 进度报告相关模式
class ProgressReportBase(BaseModel):
    """进度报告基础模式"""
    title: str = Field(..., min_length=1, max_length=200, description="报告标题")
    content: str = Field(..., min_length=1, description="报告内容")
    progress_rate: int = Field(..., ge=0, le=100, description="当前进度")
    completed_work: Optional[str] = Field(None, description="已完成工作")
    next_plan: Optional[str] = Field(None, description="下一步计划")
    issues: Optional[str] = Field(None, description="遇到的问题")
    support_needed: Optional[str] = Field(None, description="需要的支持")
    estimated_completion: Optional[datetime] = Field(None, description="预计完成时间")
    risk_assessment: Optional[str] = Field(None, description="风险评估")
    is_important: bool = Field(False, description="是否重要报告")


class ProgressReportCreate(ProgressReportBase):
    """创建进度报告"""
    supervision_item_id: UUID = Field(..., description="所属督办事项ID")
    task_assignment_id: Optional[UUID] = Field(None, description="所属任务分配ID")


class ProgressReportUpdate(BaseModel):
    """更新进度报告"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    progress_rate: Optional[int] = Field(None, ge=0, le=100)
    completed_work: Optional[str] = None
    next_plan: Optional[str] = None
    issues: Optional[str] = None
    support_needed: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    risk_assessment: Optional[str] = None
    is_important: Optional[bool] = None


class ProgressReport(ProgressReportBase):
    """进度报告响应"""
    id: UUID
    supervision_item_id: UUID
    task_assignment_id: Optional[UUID]
    reporter_id: UUID
    report_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProgressReportDetail(ProgressReport):
    """进度报告详情"""
    reporter: User


# 状态变更日志模式
class StatusLogBase(BaseModel):
    """状态变更日志基础模式"""
    action_type: str = Field(..., max_length=50, description="操作类型")
    old_status: Optional[str] = Field(None, max_length=50, description="原状态")
    new_status: str = Field(..., max_length=50, description="新状态")
    reason: Optional[str] = Field(None, description="操作原因")


class StatusLogCreate(StatusLogBase):
    """创建状态日志"""
    supervision_item_id: UUID = Field(..., description="所属督办事项ID")


class StatusLog(StatusLogBase):
    """状态变更日志响应"""
    id: UUID
    supervision_item_id: UUID
    operator_id: UUID
    action_time: datetime
    extra_data: Optional[dict]
    
    class Config:
        from_attributes = True


class StatusLogDetail(StatusLog):
    """状态变更日志详情"""
    operator: User


# 督办统计模式
class SupervisionStats(BaseModel):
    """督办统计"""
    total_count: int
    pending_count: int
    in_progress_count: int
    completed_count: int
    overdue_count: int
    completion_rate: float
    average_efficiency_score: float
    urgent_count: int
    key_count: int


class DepartmentStats(BaseModel):
    """部门统计"""
    department_id: UUID
    department_name: str
    total_count: int
    completed_count: int
    completion_rate: float
    average_score: float
    overdue_count: int


# 评价相关模式
class SupervisionEvaluationCreate(BaseModel):
    """督办评价创建"""
    quality_score: float = Field(..., ge=0, le=5, description="质量评分")
    efficiency_score: float = Field(..., ge=0, le=5, description="效率评分")
    satisfaction_score: float = Field(..., ge=0, le=5, description="满意度评分")
    evaluation_comment: Optional[str] = Field(None, description="评价意见")


class SupervisionEvaluation(BaseModel):
    """督办评价响应"""
    quality_score: float
    efficiency_score: float
    satisfaction_score: float
    overall_score: float
    evaluation_comment: Optional[str]
    evaluated_at: datetime
    evaluator_id: UUID


# 避免循环引用
SupervisionItemDetail.model_rebuild()
TaskAssignmentDetail.model_rebuild()
ProgressReportDetail.model_rebuild()
StatusLogDetail.model_rebuild()