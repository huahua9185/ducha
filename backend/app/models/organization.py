from typing import List, Optional
from uuid import UUID
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base


class Organization(Base):
    """组织机构模型"""
    __tablename__ = "organization"
    
    # 机构名称
    name: str = Column(String(100), nullable=False, comment="机构名称")
    
    # 机构代码
    code: str = Column(String(50), unique=True, nullable=False, comment="机构代码")
    
    # 机构类型（政府、部门、科室等）
    type: str = Column(String(20), nullable=False, comment="机构类型")
    
    # 机构级别
    level: int = Column(Integer, nullable=False, default=1, comment="机构级别")
    
    # 父机构ID
    parent_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('organization.id'),
        nullable=True,
        comment="父机构ID"
    )
    
    # 机构路径（便于查询）
    path: str = Column(String(500), nullable=True, comment="机构路径")
    
    # 机构描述
    description: str = Column(Text, nullable=True, comment="机构描述")
    
    # 负责人
    leader: str = Column(String(50), nullable=True, comment="负责人")
    
    # 联系电话
    phone: str = Column(String(20), nullable=True, comment="联系电话")
    
    # 办公地址
    address: str = Column(String(200), nullable=True, comment="办公地址")
    
    # 排序
    sort_order: int = Column(Integer, default=0, nullable=False, comment="排序")
    
    # 是否启用
    is_enabled: bool = Column(Boolean, default=True, nullable=False, comment="是否启用")
    
    # 关系映射
    parent: Mapped[Optional["Organization"]] = relationship("Organization", remote_side="Organization.id", back_populates="children")
    children: Mapped[List["Organization"]] = relationship("Organization", back_populates="parent")
    departments: Mapped[List["Department"]] = relationship("Department", back_populates="organization")
    
    def __repr__(self) -> str:
        return f"<Organization(name={self.name}, code={self.code})>"


class Department(Base):
    """部门模型"""
    __tablename__ = "department"
    
    # 部门名称
    name: str = Column(String(100), nullable=False, comment="部门名称")
    
    # 部门代码
    code: str = Column(String(50), unique=True, nullable=False, comment="部门代码")
    
    # 部门简称
    short_name: str = Column(String(50), nullable=True, comment="部门简称")
    
    # 所属机构ID
    organization_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('organization.id'),
        nullable=False,
        comment="所属机构ID"
    )
    
    # 父部门ID
    parent_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('department.id'),
        nullable=True,
        comment="父部门ID"
    )
    
    # 部门路径
    path: str = Column(String(500), nullable=True, comment="部门路径")
    
    # 部门级别
    level: int = Column(Integer, nullable=False, default=1, comment="部门级别")
    
    # 部门类型
    type: str = Column(String(20), nullable=False, default="department", comment="部门类型")
    
    # 部门职能描述
    function_desc: str = Column(Text, nullable=True, comment="部门职能描述")
    
    # 部门负责人ID
    manager_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=True,
        comment="部门负责人ID"
    )
    
    # 联系电话
    phone: str = Column(String(20), nullable=True, comment="联系电话")
    
    # 传真
    fax: str = Column(String(20), nullable=True, comment="传真")
    
    # 邮箱
    email: str = Column(String(100), nullable=True, comment="邮箱")
    
    # 办公地址
    address: str = Column(String(200), nullable=True, comment="办公地址")
    
    # 排序
    sort_order: int = Column(Integer, default=0, nullable=False, comment="排序")
    
    # 是否启用
    is_enabled: bool = Column(Boolean, default=True, nullable=False, comment="是否启用")
    
    # 关系映射
    organization: Mapped["Organization"] = relationship("Organization", back_populates="departments")
    parent: Mapped[Optional["Department"]] = relationship("Department", remote_side="Department.id", back_populates="children")
    children: Mapped[List["Department"]] = relationship("Department", back_populates="parent")
    manager: Mapped[Optional["User"]] = relationship("User", foreign_keys=[manager_id], back_populates="managed_departments")
    users: Mapped[List["User"]] = relationship("User", foreign_keys="User.department_id", back_populates="department")
    
    # 督办相关关系
    supervision_items: Mapped[List["SupervisionItem"]] = relationship(
        "SupervisionItem",
        foreign_keys="SupervisionItem.responsible_department_id",
        back_populates="responsible_department"
    )
    task_assignments: Mapped[List["TaskAssignment"]] = relationship(
        "TaskAssignment",
        back_populates="assigned_department"
    )
    
    def __repr__(self) -> str:
        return f"<Department(name={self.name}, code={self.code})>"