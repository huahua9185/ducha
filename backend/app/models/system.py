from datetime import datetime
from typing import Dict, Any
from uuid import UUID
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, JSON, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from enum import Enum
from .base import Base


class ConfigType(str, Enum):
    """配置类型"""
    SYSTEM = "system"         # 系统配置
    SECURITY = "security"     # 安全配置
    NOTIFICATION = "notification"  # 通知配置
    WORKFLOW = "workflow"     # 工作流配置
    INTEGRATION = "integration"  # 集成配置


class LogLevel(str, Enum):
    """日志级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SystemConfig(Base):
    """系统配置模型"""
    __tablename__ = "system_config"
    
    # 配置键
    key: str = Column(String(100), unique=True, nullable=False, comment="配置键")
    
    # 配置值
    value: str = Column(Text, nullable=True, comment="配置值")
    
    # 配置类型
    type: ConfigType = Column(
        SQLEnum(ConfigType),
        nullable=False,
        default=ConfigType.SYSTEM,
        comment="配置类型"
    )
    
    # 数据类型（string, int, float, bool, json）
    data_type: str = Column(String(20), default="string", nullable=False, comment="数据类型")
    
    # 配置名称
    name: str = Column(String(100), nullable=False, comment="配置名称")
    
    # 配置描述
    description: str = Column(Text, nullable=True, comment="配置描述")
    
    # 默认值
    default_value: str = Column(Text, nullable=True, comment="默认值")
    
    # 是否必填
    is_required: bool = Column(Boolean, default=False, nullable=False, comment="是否必填")
    
    # 是否敏感信息
    is_sensitive: bool = Column(Boolean, default=False, nullable=False, comment="是否敏感信息")
    
    # 是否启用
    is_enabled: bool = Column(Boolean, default=True, nullable=False, comment="是否启用")
    
    # 是否系统内置
    is_builtin: bool = Column(Boolean, default=False, nullable=False, comment="是否系统内置")
    
    # 排序
    sort_order: int = Column(Integer, default=0, nullable=False, comment="排序")
    
    # 验证规则（JSON）
    validation_rules: Dict[str, Any] = Column(JSON, nullable=True, comment="验证规则")
    
    # 选项列表（JSON，用于下拉选择）
    options: Dict[str, Any] = Column(JSON, nullable=True, comment="选项列表")
    
    def __repr__(self) -> str:
        return f"<SystemConfig(key={self.key}, name={self.name})>"


class OperationLog(Base):
    """操作日志模型"""
    __tablename__ = "operation_log"
    
    # 操作用户ID
    user_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=True,
        comment="操作用户ID"
    )
    
    # 用户名（冗余字段，避免用户删除后无法查看日志）
    username: str = Column(String(50), nullable=True, comment="用户名")
    
    # 真实姓名
    real_name: str = Column(String(50), nullable=True, comment="真实姓名")
    
    # 操作类型
    action_type: str = Column(String(50), nullable=False, comment="操作类型")
    
    # 操作描述
    action_desc: str = Column(String(200), nullable=False, comment="操作描述")
    
    # 模块名称
    module: str = Column(String(50), nullable=False, comment="模块名称")
    
    # 功能名称
    function: str = Column(String(50), nullable=True, comment="功能名称")
    
    # 操作对象类型
    target_type: str = Column(String(50), nullable=True, comment="操作对象类型")
    
    # 操作对象ID
    target_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        nullable=True,
        comment="操作对象ID"
    )
    
    # 操作对象名称
    target_name: str = Column(String(200), nullable=True, comment="操作对象名称")
    
    # 请求方法
    request_method: str = Column(String(10), nullable=True, comment="请求方法")
    
    # 请求URL
    request_url: str = Column(String(500), nullable=True, comment="请求URL")
    
    # 请求参数（JSON）
    request_params: Dict[str, Any] = Column(JSON, nullable=True, comment="请求参数")
    
    # 请求体（JSON）
    request_body: Dict[str, Any] = Column(JSON, nullable=True, comment="请求体")
    
    # 响应状态码
    response_status: int = Column(Integer, nullable=True, comment="响应状态码")
    
    # 响应数据（JSON）
    response_data: Dict[str, Any] = Column(JSON, nullable=True, comment="响应数据")
    
    # 执行时间（毫秒）
    execute_time: int = Column(Integer, nullable=True, comment="执行时间")
    
    # 操作结果（success, failed）
    result: str = Column(String(20), nullable=False, comment="操作结果")
    
    # 错误信息
    error_message: str = Column(Text, nullable=True, comment="错误信息")
    
    # 日志级别
    level: LogLevel = Column(
        SQLEnum(LogLevel),
        nullable=False,
        default=LogLevel.INFO,
        comment="日志级别"
    )
    
    # 客户端IP
    client_ip: str = Column(String(45), nullable=True, comment="客户端IP")
    
    # 用户代理
    user_agent: str = Column(String(500), nullable=True, comment="用户代理")
    
    # 操作时间
    operation_time: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="操作时间"
    )
    
    # 会话ID
    session_id: str = Column(String(100), nullable=True, comment="会话ID")
    
    # 追踪ID（用于分布式追踪）
    trace_id: str = Column(String(100), nullable=True, comment="追踪ID")
    
    # 扩展数据（JSON）
    extra_data: Dict[str, Any] = Column(JSON, nullable=True, comment="扩展数据")
    
    # 关系映射
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        return f"<OperationLog(username={self.username}, action_type={self.action_type})>"


class SystemSetting(Base):
    """系统设置模型"""
    __tablename__ = "system_setting"
    
    # 设置分组
    group: str = Column(String(50), nullable=False, comment="设置分组")
    
    # 设置键
    key: str = Column(String(100), nullable=False, comment="设置键")
    
    # 设置值
    value: str = Column(Text, nullable=True, comment="设置值")
    
    # 设置名称
    name: str = Column(String(100), nullable=False, comment="设置名称")
    
    # 设置描述
    description: str = Column(Text, nullable=True, comment="设置描述")
    
    # 数据类型
    data_type: str = Column(String(20), default="string", nullable=False, comment="数据类型")
    
    # 是否公开（前端可访问）
    is_public: bool = Column(Boolean, default=False, nullable=False, comment="是否公开")
    
    # 是否可编辑
    is_editable: bool = Column(Boolean, default=True, nullable=False, comment="是否可编辑")
    
    # 排序
    sort_order: int = Column(Integer, default=0, nullable=False, comment="排序")
    
    # 联合唯一约束
    __table_args__ = (
        UniqueConstraint('group', 'key', name='uq_system_setting_group_key'),
    )
    
    def __repr__(self) -> str:
        return f"<SystemSetting(group={self.group}, key={self.key})>"


class DataDictionary(Base):
    """数据字典模型"""
    __tablename__ = "data_dictionary"
    
    # 字典类型
    dict_type: str = Column(String(50), nullable=False, comment="字典类型")
    
    # 字典键
    dict_key: str = Column(String(100), nullable=False, comment="字典键")
    
    # 字典值
    dict_value: str = Column(String(200), nullable=False, comment="字典值")
    
    # 字典标签
    dict_label: str = Column(String(100), nullable=False, comment="字典标签")
    
    # 父字典键
    parent_key: str = Column(String(100), nullable=True, comment="父字典键")
    
    # 字典描述
    description: str = Column(Text, nullable=True, comment="字典描述")
    
    # 是否启用
    is_enabled: bool = Column(Boolean, default=True, nullable=False, comment="是否启用")
    
    # 是否系统内置
    is_builtin: bool = Column(Boolean, default=False, nullable=False, comment="是否系统内置")
    
    # 排序
    sort_order: int = Column(Integer, default=0, nullable=False, comment="排序")
    
    # CSS样式类
    css_class: str = Column(String(100), nullable=True, comment="CSS样式类")
    
    # 扩展属性（JSON）
    extra_attrs: Dict[str, Any] = Column(JSON, nullable=True, comment="扩展属性")
    
    # 联合唯一约束
    __table_args__ = (
        UniqueConstraint('dict_type', 'dict_key', name='uq_data_dictionary_type_key'),
    )
    
    def __repr__(self) -> str:
        return f"<DataDictionary(dict_type={self.dict_type}, dict_key={self.dict_key})>"