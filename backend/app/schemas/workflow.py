from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from uuid import UUID

from app.models.workflow import WorkflowStatus, NodeType, NodeStatus


# ========== 工作流模板相关 ==========

class WorkflowTemplateBase(BaseModel):
    """工作流模板基础Schema"""
    name: str = Field(..., description="模板名称", max_length=100)
    code: str = Field(..., description="模板代码", max_length=50)
    description: Optional[str] = Field(None, description="模板描述")
    type: str = Field(..., description="模板类型", max_length=50)
    version: Optional[str] = Field("1.0", description="版本号", max_length=20)
    is_enabled: bool = Field(True, description="是否启用")
    definition: Dict[str, Any] = Field(..., description="工作流定义")
    form_config: Optional[Dict[str, Any]] = Field(None, description="表单配置")
    permission_config: Optional[Dict[str, Any]] = Field(None, description="权限配置")
    notification_config: Optional[Dict[str, Any]] = Field(None, description="通知配置")
    sort_order: int = Field(0, description="排序")


class WorkflowTemplateCreate(WorkflowTemplateBase):
    """创建工作流模板Schema"""
    pass


class WorkflowTemplateUpdate(BaseModel):
    """更新工作流模板Schema"""
    name: Optional[str] = Field(None, description="模板名称", max_length=100)
    description: Optional[str] = Field(None, description="模板描述")
    is_enabled: Optional[bool] = Field(None, description="是否启用")
    definition: Optional[Dict[str, Any]] = Field(None, description="工作流定义")
    form_config: Optional[Dict[str, Any]] = Field(None, description="表单配置")
    permission_config: Optional[Dict[str, Any]] = Field(None, description="权限配置")
    notification_config: Optional[Dict[str, Any]] = Field(None, description="通知配置")
    sort_order: Optional[int] = Field(None, description="排序")


class WorkflowTemplateResponse(WorkflowTemplateBase):
    """工作流模板响应Schema"""
    id: UUID
    is_builtin: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ========== 工作流实例相关 ==========

class WorkflowInstanceBase(BaseModel):
    """工作流实例基础Schema"""
    title: str = Field(..., description="实例标题", max_length=200)
    business_id: Optional[UUID] = Field(None, description="关联业务ID")
    business_type: Optional[str] = Field(None, description="业务类型", max_length=50)
    business_data: Optional[Dict[str, Any]] = Field(None, description="业务数据")
    variables: Optional[Dict[str, Any]] = Field(None, description="变量数据")
    priority: int = Field(1, description="优先级", ge=1, le=5)


class WorkflowInstanceCreate(WorkflowInstanceBase):
    """创建工作流实例Schema"""
    template_id: UUID = Field(..., description="模板ID")


class WorkflowInstanceUpdate(BaseModel):
    """更新工作流实例Schema"""
    title: Optional[str] = Field(None, description="实例标题", max_length=200)
    business_data: Optional[Dict[str, Any]] = Field(None, description="业务数据")
    variables: Optional[Dict[str, Any]] = Field(None, description="变量数据")
    priority: Optional[int] = Field(None, description="优先级", ge=1, le=5)


class WorkflowInstanceResponse(WorkflowInstanceBase):
    """工作流实例响应Schema"""
    id: UUID
    number: str
    template_id: UUID
    initiator_id: UUID
    status: WorkflowStatus
    current_nodes: Optional[List[str]]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ========== 工作流节点相关 ==========

class WorkflowNodeBase(BaseModel):
    """工作流节点基础Schema"""
    name: str = Field(..., description="节点名称", max_length=100)
    type: NodeType = Field(..., description="节点类型")
    assignee_id: Optional[UUID] = Field(None, description="分配给用户ID")
    assignee_role_id: Optional[UUID] = Field(None, description="分配给角色ID")
    assignee_department_id: Optional[UUID] = Field(None, description="分配给部门ID")
    deadline: Optional[datetime] = Field(None, description="截止时间")
    node_data: Optional[Dict[str, Any]] = Field(None, description="节点数据")


class WorkflowNodeCreate(WorkflowNodeBase):
    """创建工作流节点Schema"""
    workflow_instance_id: UUID = Field(..., description="工作流实例ID")
    node_id: str = Field(..., description="节点ID", max_length=50)


class WorkflowNodeUpdate(BaseModel):
    """更新工作流节点Schema"""
    form_data: Optional[Dict[str, Any]] = Field(None, description="表单数据")
    comment: Optional[str] = Field(None, description="处理意见")


class WorkflowNodeResponse(WorkflowNodeBase):
    """工作流节点响应Schema"""
    id: UUID
    workflow_instance_id: UUID
    node_id: str
    status: NodeStatus
    processor_id: Optional[UUID]
    enter_time: Optional[datetime]
    start_time: Optional[datetime]
    complete_time: Optional[datetime]
    form_data: Optional[Dict[str, Any]]
    comment: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ========== 工作流转换相关 ==========

class WorkflowTransitionResponse(BaseModel):
    """工作流转换响应Schema"""
    id: UUID
    workflow_instance_id: UUID
    from_node_id: Optional[str]
    to_node_id: str
    name: Optional[str]
    condition: Optional[str]
    executor_id: Optional[UUID]
    execute_time: datetime
    transition_data: Optional[Dict[str, Any]]
    comment: Optional[str]
    
    class Config:
        from_attributes = True


# ========== 任务处理相关 ==========

class TaskCompleteRequest(BaseModel):
    """任务完成请求Schema"""
    form_data: Optional[Dict[str, Any]] = Field(None, description="表单数据")
    comment: Optional[str] = Field(None, description="处理意见", max_length=1000)
    result: Optional[str] = Field(None, description="处理结果", max_length=20)


class TaskListQuery(BaseModel):
    """任务列表查询Schema"""
    page: int = Field(1, description="页码", ge=1)
    size: int = Field(20, description="每页数量", ge=1, le=100)
    status: Optional[NodeStatus] = Field(None, description="任务状态")
    keyword: Optional[str] = Field(None, description="关键词", max_length=100)


# ========== 统计信息相关 ==========

class WorkflowStats(BaseModel):
    """工作流统计信息"""
    total_templates: int = Field(0, description="模板总数")
    active_templates: int = Field(0, description="激活模板数")
    total_instances: int = Field(0, description="实例总数")
    running_instances: int = Field(0, description="运行中实例数")
    completed_instances: int = Field(0, description="已完成实例数")
    pending_tasks: int = Field(0, description="待处理任务数")
    overdue_tasks: int = Field(0, description="逾期任务数")


class UserTaskStats(BaseModel):
    """用户任务统计"""
    pending_tasks: int = Field(0, description="待处理任务")
    processing_tasks: int = Field(0, description="处理中任务")
    completed_tasks: int = Field(0, description="已完成任务")
    overdue_tasks: int = Field(0, description="逾期任务")


# ========== 分页响应 ==========

class WorkflowTemplateListResponse(BaseModel):
    """工作流模板列表响应"""
    items: List[WorkflowTemplateResponse]
    total: int
    page: int
    size: int
    pages: int


class WorkflowInstanceListResponse(BaseModel):
    """工作流实例列表响应"""
    items: List[WorkflowInstanceResponse]
    total: int
    page: int
    size: int
    pages: int


class WorkflowNodeListResponse(BaseModel):
    """工作流节点列表响应"""
    items: List[WorkflowNodeResponse]
    total: int
    page: int
    size: int
    pages: int