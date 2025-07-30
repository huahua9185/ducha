from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Table, Integer
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from .base import Base


# 用户角色关联表
user_role_table = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', PostgreSQLUUID(as_uuid=True), ForeignKey('user.id'), primary_key=True),
    Column('role_id', PostgreSQLUUID(as_uuid=True), ForeignKey('role.id'), primary_key=True)
)

# 角色权限关联表
role_permission_table = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', PostgreSQLUUID(as_uuid=True), ForeignKey('role.id'), primary_key=True),
    Column('permission_id', PostgreSQLUUID(as_uuid=True), ForeignKey('permission.id'), primary_key=True)
)


class User(Base):
    """用户模型"""
    __tablename__ = "user"
    
    # 用户名（登录用）
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    
    # 真实姓名
    real_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="真实姓名")
    
    # 密码哈希
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")
    
    # 邮箱
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, comment="邮箱")
    
    # 手机号
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="手机号")
    
    # 工号
    employee_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, comment="工号")
    
    # 职位
    position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="职位")
    
    # 部门ID
    department_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('department.id'),
        nullable=True,
        comment="部门ID"
    )
    
    # 上级领导ID
    superior_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=True,
        comment="上级领导ID"
    )
    
    # 头像URL
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="头像URL")
    
    # 是否激活
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="是否激活")
    
    # 是否超级管理员
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否超级管理员")
    
    # 最后登录时间
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="最后登录时间")
    
    # 登录IP
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True, comment="最后登录IP")
    
    # 个人简介
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="个人简介")
    
    # 工作年限
    work_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="工作年限")
    
    # 联系地址
    address: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="联系地址")
    
    # 关系映射
    department: Mapped[Optional["Department"]] = relationship("Department", foreign_keys=[department_id], back_populates="users")
    managed_departments: Mapped[List["Department"]] = relationship("Department", foreign_keys="Department.manager_id", back_populates="manager")
    superior: Mapped[Optional["User"]] = relationship("User", remote_side="User.id", back_populates="subordinates")
    subordinates: Mapped[List["User"]] = relationship("User", back_populates="superior")
    roles: Mapped[List["Role"]] = relationship("Role", secondary=user_role_table, back_populates="users")
    
    # 督办相关关系
    created_supervisions: Mapped[List["SupervisionItem"]] = relationship(
        "SupervisionItem", 
        foreign_keys="SupervisionItem.creator_id",
        back_populates="creator"
    )
    assigned_tasks: Mapped[List["TaskAssignment"]] = relationship(
        "TaskAssignment",
        back_populates="assignee"
    )
    progress_reports: Mapped[List["ProgressReport"]] = relationship(
        "ProgressReport",
        back_populates="reporter"
    )
    
    def __repr__(self) -> str:
        return f"<User(username={self.username}, real_name={self.real_name})>"


class Role(Base):
    """角色模型"""
    __tablename__ = "role"
    
    # 角色名称
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="角色名称")
    
    # 角色代码
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="角色代码")
    
    # 角色描述
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="角色描述")
    
    # 是否系统内置角色
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否系统内置角色")
    
    # 排序
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序")
    
    # 关系映射
    users: Mapped[List["User"]] = relationship("User", secondary=user_role_table, back_populates="roles")
    permissions: Mapped[List["Permission"]] = relationship("Permission", secondary=role_permission_table, back_populates="roles")
    
    def __repr__(self) -> str:
        return f"<Role(name={self.name}, code={self.code})>"


class Permission(Base):
    """权限模型"""
    __tablename__ = "permission"
    
    # 权限名称
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="权限名称")
    
    # 权限代码
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="权限代码")
    
    # 权限描述
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="权限描述")
    
    # 权限类型（菜单、按钮、数据等）
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="action", comment="权限类型")
    
    # 父权限ID
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('permission.id'),
        nullable=True,
        comment="父权限ID"
    )
    
    # 路径（用于树形结构）
    path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="权限路径")
    
    # 图标
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="图标")
    
    # 排序
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序")
    
    # 是否启用
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="是否启用")
    
    # 关系映射
    parent: Mapped[Optional["Permission"]] = relationship("Permission", remote_side="Permission.id", back_populates="children")
    children: Mapped[List["Permission"]] = relationship("Permission", back_populates="parent")
    roles: Mapped[List["Role"]] = relationship("Role", secondary=role_permission_table, back_populates="permissions")
    
    def __repr__(self) -> str:
        return f"<Permission(name={self.name}, code={self.code})>"


class UserRole(Base):
    """用户角色关联模型（扩展字段）"""
    __tablename__ = "user_role"
    
    # 用户ID
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=False,
        comment="用户ID"
    )
    
    # 角色ID
    role_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('role.id'),
        nullable=False,
        comment="角色ID"
    )
    
    # 分配者ID
    assigned_by: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=True,
        comment="分配者ID"
    )
    
    # 分配时间
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="分配时间"
    )
    
    # 过期时间
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="过期时间"
    )
    
    # 是否激活
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="是否激活")
    
    # 关系映射
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    role: Mapped["Role"] = relationship("Role", foreign_keys=[role_id])
    assigner: Mapped["User"] = relationship("User", foreign_keys=[assigned_by])
    
    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"