from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.security import get_password_hash
from app.models.user import User, Role, Permission, user_role_table, role_permission_table
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: UUID) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id, User.is_deleted == False).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(
        User.username == username, 
        User.is_deleted == False
    ).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(
        User.email == email, 
        User.is_deleted == False
    ).first()


def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    search: str = None,
    department_id: UUID = None,
    is_active: bool = None
) -> List[User]:
    """获取用户列表"""
    query = db.query(User).filter(User.is_deleted == False)
    
    if search:
        query = query.filter(
            or_(
                User.username.contains(search),
                User.real_name.contains(search),
                User.email.contains(search)
            )
        )
    
    if department_id:
        query = query.filter(User.department_id == department_id)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


def count_users(
    db: Session,
    search: str = None,
    department_id: UUID = None,
    is_active: bool = None
) -> int:
    """统计用户数量"""
    query = db.query(User).filter(User.is_deleted == False)
    
    if search:
        query = query.filter(
            or_(
                User.username.contains(search),
                User.real_name.contains(search),
                User.email.contains(search)
            )
        )
    
    if department_id:
        query = query.filter(User.department_id == department_id)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.count()


def create_user(db: Session, user_create: UserCreate) -> User:
    """创建用户"""
    hashed_password = get_password_hash(user_create.password)
    
    db_user = User(
        username=user_create.username,
        real_name=user_create.real_name,
        email=user_create.email,
        phone=user_create.phone,
        employee_id=user_create.employee_id,
        position=user_create.position,
        department_id=user_create.department_id,
        superior_id=user_create.superior_id,
        avatar_url=user_create.avatar_url,
        bio=user_create.bio,
        work_years=user_create.work_years,
        address=user_create.address,
        password_hash=hashed_password,
        is_active=True,
        is_superuser=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
    """更新用户"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def update_password(db: Session, user_id: UUID, new_password: str) -> Optional[User]:
    """更新用户密码"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.password_hash = get_password_hash(new_password)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: UUID) -> bool:
    """删除用户（软删除）"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db_user.is_deleted = True
    db_user.deleted_at = datetime.utcnow()
    db.commit()
    return True


def activate_user(db: Session, user_id: UUID) -> Optional[User]:
    """激活用户"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.is_active = True
    db.commit()
    db.refresh(db_user)
    return db_user


def deactivate_user(db: Session, user_id: UUID) -> Optional[User]:
    """停用用户"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.is_active = False
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_roles(db: Session, user_id: UUID) -> List[Role]:
    """获取用户角色"""
    return db.query(Role).join(user_role_table).filter(
        user_role_table.c.user_id == user_id
    ).all()


def get_user_permissions(db: Session, user_id: UUID) -> List[str]:
    """获取用户权限"""
    permissions = db.query(Permission.code).join(role_permission_table).join(
        user_role_table, role_permission_table.c.role_id == user_role_table.c.role_id
    ).filter(
        user_role_table.c.user_id == user_id,
        Permission.is_enabled == True
    ).distinct().all()
    
    return [p.code for p in permissions]


def assign_roles(db: Session, user_id: UUID, role_ids: List[UUID]) -> bool:
    """分配用户角色"""
    # 删除现有角色
    db.execute(
        user_role_table.delete().where(user_role_table.c.user_id == user_id)
    )
    
    # 添加新角色
    if role_ids:
        values = [{"user_id": user_id, "role_id": role_id} for role_id in role_ids]
        db.execute(user_role_table.insert().values(values))
    
    db.commit()
    return True


def remove_role(db: Session, user_id: UUID, role_id: UUID) -> bool:
    """移除用户角色"""
    db.execute(
        user_role_table.delete().where(
            and_(
                user_role_table.c.user_id == user_id,
                user_role_table.c.role_id == role_id
            )
        )
    )
    db.commit()
    return True


def get_subordinates(db: Session, user_id: UUID) -> List[User]:
    """获取下属用户"""
    return db.query(User).filter(
        User.superior_id == user_id,
        User.is_deleted == False
    ).all()


def get_department_users(db: Session, department_id: UUID) -> List[User]:
    """获取部门用户"""
    return db.query(User).filter(
        User.department_id == department_id,
        User.is_deleted == False
    ).all()


def check_username_exists(db: Session, username: str, exclude_user_id: UUID = None) -> bool:
    """检查用户名是否存在"""
    query = db.query(User).filter(
        User.username == username,
        User.is_deleted == False
    )
    
    if exclude_user_id:
        query = query.filter(User.id != exclude_user_id)
    
    return query.first() is not None


def check_email_exists(db: Session, email: str, exclude_user_id: UUID = None) -> bool:
    """检查邮箱是否存在"""
    query = db.query(User).filter(
        User.email == email,
        User.is_deleted == False
    )
    
    if exclude_user_id:
        query = query.filter(User.id != exclude_user_id)
    
    return query.first() is not None


# 角色管理
def get_role(db: Session, role_id: UUID) -> Optional[Role]:
    """根据ID获取角色"""
    return db.query(Role).filter(Role.id == role_id, Role.is_deleted == False).first()


def get_role_by_code(db: Session, code: str) -> Optional[Role]:
    """根据代码获取角色"""
    return db.query(Role).filter(
        Role.code == code, 
        Role.is_deleted == False
    ).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    """获取角色列表"""
    return db.query(Role).filter(Role.is_deleted == False).offset(skip).limit(limit).all()


def count_roles(db: Session) -> int:
    """统计角色数量"""
    return db.query(Role).filter(Role.is_deleted == False).count()


# 权限管理
def get_permission(db: Session, permission_id: UUID) -> Optional[Permission]:
    """根据ID获取权限"""
    return db.query(Permission).filter(
        Permission.id == permission_id, 
        Permission.is_deleted == False
    ).first()


def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[Permission]:
    """获取权限列表"""
    return db.query(Permission).filter(Permission.is_deleted == False).offset(skip).limit(limit).all()


def get_permission_tree(db: Session) -> List[Permission]:
    """获取权限树"""
    return db.query(Permission).filter(
        Permission.is_deleted == False,
        Permission.parent_id.is_(None)
    ).order_by(Permission.sort_order).all()