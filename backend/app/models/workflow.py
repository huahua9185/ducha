from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from enum import Enum
from .base import Base


class WorkflowStatus(str, Enum):
    """工作流状态"""
    DRAFT = "draft"           # 草稿
    ACTIVE = "active"         # 激活
    SUSPENDED = "suspended"   # 暂停
    COMPLETED = "completed"   # 完成
    TERMINATED = "terminated" # 终止


class NodeType(str, Enum):
    """节点类型"""
    START = "start"           # 开始节点
    END = "end"              # 结束节点
    TASK = "task"            # 任务节点
    DECISION = "decision"     # 决策节点
    PARALLEL = "parallel"     # 并行节点
    MERGE = "merge"          # 合并节点


class NodeStatus(str, Enum):
    """节点状态"""
    PENDING = "pending"       # 待处理
    ACTIVE = "active"         # 激活
    COMPLETED = "completed"   # 完成
    SKIPPED = "skipped"       # 跳过
    FAILED = "failed"         # 失败


class WorkflowTemplate(Base):
    """工作流模板模型"""
    __tablename__ = "workflow_template"
    
    # 模板名称
    name: str = Column(String(100), nullable=False, comment="模板名称")
    
    # 模板代码
    code: str = Column(String(50), unique=True, nullable=False, comment="模板代码")
    
    # 模板描述
    description: str = Column(Text, nullable=True, comment="模板描述")
    
    # 模板类型
    type: str = Column(String(50), nullable=False, comment="模板类型")
    
    # 版本号
    version: str = Column(String(20), nullable=False, default="1.0", comment="版本号")
    
    # 是否启用
    is_enabled: bool = Column(Boolean, default=True, nullable=False, comment="是否启用")
    
    # 是否系统内置
    is_builtin: bool = Column(Boolean, default=False, nullable=False, comment="是否系统内置")
    
    # 工作流定义（JSON）
    definition: Dict[str, Any] = Column(JSON, nullable=False, comment="工作流定义")
    
    # 表单配置（JSON）
    form_config: Dict[str, Any] = Column(JSON, nullable=True, comment="表单配置")
    
    # 权限配置（JSON）
    permission_config: Dict[str, Any] = Column(JSON, nullable=True, comment="权限配置")
    
    # 通知配置（JSON）
    notification_config: Dict[str, Any] = Column(JSON, nullable=True, comment="通知配置")
    
    # 排序
    sort_order: int = Column(Integer, default=0, nullable=False, comment="排序")
    
    # 关系映射
    workflow_instances: Mapped[List["WorkflowInstance"]] = relationship("WorkflowInstance", back_populates="template")
    
    def __repr__(self) -> str:
        return f"<WorkflowTemplate(name={self.name}, code={self.code})>"


class WorkflowInstance(Base):
    """工作流实例模型"""
    __tablename__ = "workflow_instance"
    
    # 实例编号
    number: str = Column(String(50), unique=True, nullable=False, comment="实例编号")
    
    # 实例标题
    title: str = Column(String(200), nullable=False, comment="实例标题")
    
    # 模板ID
    template_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('workflow_template.id'),
        nullable=False,
        comment="模板ID"
    )
    
    # 发起人ID
    initiator_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=False,
        comment="发起人ID"
    )
    
    # 关联业务ID（如督办事项ID）
    business_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        nullable=True,
        comment="关联业务ID"
    )
    
    # 业务类型
    business_type: str = Column(String(50), nullable=True, comment="业务类型")
    
    # 工作流状态
    status: WorkflowStatus = Column(
        SQLEnum(WorkflowStatus),
        nullable=False,
        default=WorkflowStatus.DRAFT,
        comment="工作流状态"
    )
    
    # 当前节点ID列表（JSON）
    current_nodes: List[str] = Column(JSON, nullable=True, comment="当前节点ID列表")
    
    # 开始时间
    start_time: datetime = Column(DateTime(timezone=True), nullable=True, comment="开始时间")
    
    # 结束时间
    end_time: datetime = Column(DateTime(timezone=True), nullable=True, comment="结束时间")
    
    # 业务数据（JSON）
    business_data: Dict[str, Any] = Column(JSON, nullable=True, comment="业务数据")
    
    # 变量数据（JSON）
    variables: Dict[str, Any] = Column(JSON, nullable=True, comment="变量数据")
    
    # 优先级
    priority: int = Column(Integer, default=1, nullable=False, comment="优先级")
    
    # 关系映射
    template: Mapped["WorkflowTemplate"] = relationship("WorkflowTemplate", back_populates="workflow_instances")
    initiator: Mapped["User"] = relationship("User")
    nodes: Mapped[List["WorkflowNode"]] = relationship("WorkflowNode", back_populates="workflow_instance", cascade="all, delete-orphan")
    transitions: Mapped[List["WorkflowTransition"]] = relationship("WorkflowTransition", back_populates="workflow_instance", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<WorkflowInstance(number={self.number}, title={self.title})>"


class WorkflowNode(Base):
    """工作流节点实例模型"""
    __tablename__ = "workflow_node"
    
    # 工作流实例ID
    workflow_instance_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('workflow_instance.id'),
        nullable=False,
        comment="工作流实例ID"
    )
    
    # 节点ID（在模板中的ID）
    node_id: str = Column(String(50), nullable=False, comment="节点ID")
    
    # 节点名称
    name: str = Column(String(100), nullable=False, comment="节点名称")
    
    # 节点类型
    type: NodeType = Column(
        SQLEnum(NodeType),
        nullable=False,
        comment="节点类型"
    )
    
    # 节点状态
    status: NodeStatus = Column(
        SQLEnum(NodeStatus),
        nullable=False,
        default=NodeStatus.PENDING,
        comment="节点状态"
    )
    
    # 分配给用户ID
    assignee_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=True,
        comment="分配给用户ID"
    )
    
    # 分配给角色ID
    assignee_role_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('role.id'),
        nullable=True,
        comment="分配给角色ID"
    )
    
    # 分配给部门ID
    assignee_department_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('department.id'),
        nullable=True,
        comment="分配给部门ID"
    )
    
    # 实际处理人ID
    processor_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=True,
        comment="实际处理人ID"
    )
    
    # 进入时间
    enter_time: datetime = Column(DateTime(timezone=True), nullable=True, comment="进入时间")
    
    # 开始处理时间
    start_time: datetime = Column(DateTime(timezone=True), nullable=True, comment="开始处理时间")
    
    # 完成时间
    complete_time: datetime = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    
    # 截止时间
    deadline: datetime = Column(DateTime(timezone=True), nullable=True, comment="截止时间")
    
    # 节点数据（JSON）
    node_data: Dict[str, Any] = Column(JSON, nullable=True, comment="节点数据")
    
    # 表单数据（JSON）
    form_data: Dict[str, Any] = Column(JSON, nullable=True, comment="表单数据")
    
    # 处理意见
    comment: str = Column(Text, nullable=True, comment="处理意见")
    
    # 关系映射
    workflow_instance: Mapped["WorkflowInstance"] = relationship("WorkflowInstance", back_populates="nodes")
    assignee: Mapped["User"] = relationship("User", foreign_keys=[assignee_id])
    assignee_role: Mapped["Role"] = relationship("Role")
    assignee_department: Mapped["Department"] = relationship("Department")
    processor: Mapped["User"] = relationship("User", foreign_keys=[processor_id])
    
    def __repr__(self) -> str:
        return f"<WorkflowNode(node_id={self.node_id}, name={self.name})>"


class WorkflowTransition(Base):
    """工作流转换记录模型"""
    __tablename__ = "workflow_transition"
    
    # 工作流实例ID
    workflow_instance_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('workflow_instance.id'),
        nullable=False,
        comment="工作流实例ID"
    )
    
    # 源节点ID
    from_node_id: str = Column(String(50), nullable=True, comment="源节点ID")
    
    # 目标节点ID
    to_node_id: str = Column(String(50), nullable=False, comment="目标节点ID")
    
    # 转换名称
    name: str = Column(String(100), nullable=True, comment="转换名称")
    
    # 转换条件
    condition: str = Column(Text, nullable=True, comment="转换条件")
    
    # 执行人ID
    executor_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=True,
        comment="执行人ID"
    )
    
    # 执行时间
    execute_time: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="执行时间"
    )
    
    # 转换数据（JSON）
    transition_data: Dict[str, Any] = Column(JSON, nullable=True, comment="转换数据")
    
    # 备注
    comment: str = Column(Text, nullable=True, comment="备注")
    
    # 关系映射
    workflow_instance: Mapped["WorkflowInstance"] = relationship("WorkflowInstance", back_populates="transitions")
    executor: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        return f"<WorkflowTransition(from_node_id={self.from_node_id}, to_node_id={self.to_node_id})>"