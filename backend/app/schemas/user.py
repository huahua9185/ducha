from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    real_name: str = Field(..., min_length=1, max_length=50, description="真实姓名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    employee_id: Optional[str] = Field(None, max_length=50, description="工号")
    position: Optional[str] = Field(None, max_length=100, description="职位")
    department_id: Optional[UUID] = Field(None, description="部门ID")
    superior_id: Optional[UUID] = Field(None, description="上级ID")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    bio: Optional[str] = Field(None, description="个人简介")
    work_years: Optional[int] = Field(None, ge=0, description="工作年限")
    address: Optional[str] = Field(None, max_length=200, description="联系地址")


class UserCreate(UserBase):
    """创建用户"""
    password: str = Field(..., min_length=8, description="密码")


class UserUpdate(BaseModel):
    """更新用户"""
    real_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    employee_id: Optional[str] = Field(None, max_length=50)
    position: Optional[str] = Field(None, max_length=100)
    department_id: Optional[UUID] = None
    superior_id: Optional[UUID] = None
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = None
    work_years: Optional[int] = Field(None, ge=0)
    address: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


class User(UserBase):
    """用户响应"""
    id: UUID
    is_active: bool
    is_superuser: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserWithRoles(User):
    """包含角色的用户"""
    roles: List["Role"] = []


class UserWithPermissions(User):
    """包含权限的用户"""
    permissions: List[str] = []


class UserInDB(User):
    """数据库中的用户"""
    password_hash: str


class UserList(BaseModel):
    """用户列表响应"""
    items: List[User]
    total: int
    page: int
    size: int
    pages: int


# 角色相关模式
class RoleBase(BaseModel):
    """角色基础模式"""
    name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    code: str = Field(..., min_length=1, max_length=50, description="角色代码")
    description: Optional[str] = Field(None, description="角色描述")
    sort_order: int = Field(0, description="排序")


class RoleCreate(RoleBase):
    """创建角色"""
    pass


class RoleUpdate(BaseModel):
    """更新角色"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    sort_order: Optional[int] = None


class Role(RoleBase):
    """角色响应"""
    id: UUID
    is_builtin: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoleWithPermissions(Role):
    """包含权限的角色"""
    permissions: List["Permission"] = []


class RoleList(BaseModel):
    """角色列表响应"""
    items: List[Role]
    total: int
    page: int
    size: int
    pages: int


# 权限相关模式
class PermissionBase(BaseModel):
    """权限基础模式"""
    name: str = Field(..., min_length=1, max_length=100, description="权限名称")
    code: str = Field(..., min_length=1, max_length=100, description="权限代码")
    description: Optional[str] = Field(None, description="权限描述")
    type: str = Field("action", description="权限类型")
    parent_id: Optional[UUID] = Field(None, description="父权限ID")
    path: Optional[str] = Field(None, max_length=500, description="权限路径")
    icon: Optional[str] = Field(None, max_length=100, description="图标")
    sort_order: int = Field(0, description="排序")


class PermissionCreate(PermissionBase):
    """创建权限"""
    pass


class PermissionUpdate(BaseModel):
    """更新权限"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    type: Optional[str] = None
    parent_id: Optional[UUID] = None
    path: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    sort_order: Optional[int] = None
    is_enabled: Optional[bool] = None


class Permission(PermissionBase):
    """权限响应"""
    id: UUID
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PermissionTree(Permission):
    """权限树"""
    children: List["PermissionTree"] = []


class PermissionList(BaseModel):
    """权限列表响应"""
    items: List[Permission]
    total: int
    page: int
    size: int
    pages: int


# 用户角色分配
class UserRoleAssign(BaseModel):
    """用户角色分配"""
    user_id: UUID
    role_ids: List[UUID]


class RolePermissionAssign(BaseModel):
    """角色权限分配"""
    role_id: UUID
    permission_ids: List[UUID]


# 避免循环导入
PermissionTree.model_rebuild()
UserWithRoles.model_rebuild()
RoleWithPermissions.model_rebuild()