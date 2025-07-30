from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, BigInteger, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from .base import Base


class Attachment(Base):
    """附件模型"""
    __tablename__ = "attachment"
    
    # 文件名
    filename: str = Column(String(255), nullable=False, comment="文件名")
    
    # 原始文件名
    original_filename: str = Column(String(255), nullable=False, comment="原始文件名")
    
    # 文件路径
    file_path: str = Column(String(500), nullable=False, comment="文件路径")
    
    # 文件大小（字节）
    file_size: int = Column(BigInteger, nullable=False, comment="文件大小")
    
    # 文件类型（MIME类型）
    content_type: str = Column(String(100), nullable=False, comment="文件类型")
    
    # 文件扩展名
    file_extension: str = Column(String(10), nullable=True, comment="文件扩展名")
    
    # 文件哈希值（用于去重和完整性检查）
    file_hash: str = Column(String(64), nullable=True, comment="文件哈希值")
    
    # 上传者ID
    uploader_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=False,
        comment="上传者ID"
    )
    
    # 关联督办事项ID
    supervision_item_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('supervision_item.id'),
        nullable=True,
        comment="关联督办事项ID"
    )
    
    # 关联进度报告ID
    progress_report_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('progress_report.id'),
        nullable=True,
        comment="关联进度报告ID"
    )
    
    # 关联业务类型
    related_type: str = Column(String(50), nullable=True, comment="关联业务类型")
    
    # 关联业务ID
    related_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        nullable=True,
        comment="关联业务ID"
    )
    
    # 文件分类
    category: str = Column(String(50), nullable=True, comment="文件分类")
    
    # 文件描述
    description: str = Column(Text, nullable=True, comment="文件描述")
    
    # 是否公开
    is_public: bool = Column(Boolean, default=False, nullable=False, comment="是否公开")
    
    # 是否临时文件
    is_temporary: bool = Column(Boolean, default=False, nullable=False, comment="是否临时文件")
    
    # 下载次数
    download_count: int = Column(Integer, default=0, nullable=False, comment="下载次数")
    
    # 最后下载时间
    last_download_at: datetime = Column(DateTime(timezone=True), nullable=True, comment="最后下载时间")
    
    # 缩略图路径（用于图片文件）
    thumbnail_path: str = Column(String(500), nullable=True, comment="缩略图路径")
    
    # 预览URL
    preview_url: str = Column(String(500), nullable=True, comment="预览URL")
    
    # 存储类型（local, oss, s3等）
    storage_type: str = Column(String(20), default="local", nullable=False, comment="存储类型")
    
    # 存储配置（JSON）
    storage_config: dict = Column(JSON, nullable=True, comment="存储配置")
    
    # 是否已病毒扫描
    virus_scanned: bool = Column(Boolean, default=False, nullable=False, comment="是否已病毒扫描")
    
    # 病毒扫描结果
    virus_scan_result: str = Column(String(50), nullable=True, comment="病毒扫描结果")
    
    # 关系映射
    uploader: Mapped["User"] = relationship("User")
    supervision_item: Mapped["SupervisionItem"] = relationship("SupervisionItem", back_populates="attachments")
    progress_report: Mapped["ProgressReport"] = relationship("ProgressReport", back_populates="attachments")
    
    def __repr__(self) -> str:
        return f"<Attachment(filename={self.filename}, uploader_id={self.uploader_id})>"


class AttachmentPermission(Base):
    """附件权限模型"""
    __tablename__ = "attachment_permission"
    
    # 附件ID
    attachment_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('attachment.id'),
        nullable=False,
        comment="附件ID"
    )
    
    # 用户ID
    user_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=True,
        comment="用户ID"
    )
    
    # 角色ID
    role_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('role.id'),
        nullable=True,
        comment="角色ID"
    )
    
    # 部门ID
    department_id: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('department.id'),
        nullable=True,
        comment="部门ID"
    )
    
    # 权限类型（view, download, edit, delete）
    permission_type: str = Column(String(20), nullable=False, comment="权限类型")
    
    # 是否允许
    is_allowed: bool = Column(Boolean, default=True, nullable=False, comment="是否允许")
    
    # 授权者ID
    granted_by: UUID = Column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=True,
        comment="授权者ID"
    )
    
    # 授权时间
    granted_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="授权时间"
    )
    
    # 过期时间
    expires_at: datetime = Column(DateTime(timezone=True), nullable=True, comment="过期时间")
    
    # 关系映射
    attachment: Mapped["Attachment"] = relationship("Attachment")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    role: Mapped["Role"] = relationship("Role")
    department: Mapped["Department"] = relationship("Department")
    granter: Mapped["User"] = relationship("User", foreign_keys=[granted_by])
    
    def __repr__(self) -> str:
        return f"<AttachmentPermission(attachment_id={self.attachment_id}, permission_type={self.permission_type})>"