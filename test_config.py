#!/usr/bin/env python3
"""
简化测试配置
使用SQLite数据库进行测试
"""

import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

# 设置测试数据库URL
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["TESTING"] = "true"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.db.base import Base
from backend.app.models.user import User
from backend.app.models.organization import Department, Role
from backend.app.models.supervision import SupervisionItem, SupervisionStatus, UrgencyLevel, SupervisionType
from backend.app.core.security import get_password_hash

# 创建SQLite引擎
engine = create_engine("sqlite:///./test.db", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_test_db():
    """初始化测试数据库"""
    print("🔧 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")

def create_test_data():
    """创建测试数据"""
    print("🚀 开始创建测试数据...")
    
    db = SessionLocal()
    
    try:
        # 1. 创建部门
        dept1 = Department(
            name="市政府办公室",
            code="OFFICE",  
            description="市政府办公室",
            level=1,
            sort_order=1,
            is_active=True
        )
        dept2 = Department(
            name="发展改革委",
            code="DRC",
            description="发展和改革委员会", 
            level=1,
            sort_order=2,
            is_active=True
        )
        
        db.add(dept1)
        db.add(dept2)
        db.commit()
        
        # 2. 创建角色
        role_admin = Role(
            name="系统管理员",
            code="ADMIN",
            description="系统管理员，拥有所有权限",
            is_builtin=True,
            sort_order=1
        )
        role_user = Role(
            name="普通用户", 
            code="USER",
            description="普通用户，处理分配的任务",
            is_builtin=True,
            sort_order=2
        )
        
        db.add(role_admin)
        db.add(role_user)
        db.commit()
        
        # 3. 创建用户
        admin_user = User(
            username="admin",
            real_name="系统管理员",
            email="admin@example.com",
            phone="13800138000", 
            employee_id="ADMIN001",
            position="系统管理员",
            password_hash=get_password_hash("admin123456"),
            department_id=dept1.id,
            is_active=True,
            is_superuser=True
        )
        
        test_user = User(
            username="test_admin",
            real_name="测试管理员", 
            email="admin@test.com",
            phone="13800138001",
            employee_id="TEST001", 
            position="测试员",
            password_hash=get_password_hash("test123456"),
            department_id=dept1.id,
            is_active=True,
            is_superuser=True
        )
        
        db.add(admin_user)
        db.add(test_user)
        db.commit()
        
        # 4. 创建督办事项
        supervision_item = SupervisionItem(
            number="DB20250001",
            title="推进重大项目建设进度",
            content="督办各部门重大项目建设进度，确保按时完成年度目标任务。",
            type=SupervisionType.KEY,
            urgency=UrgencyLevel.HIGH,
            status=SupervisionStatus.IN_PROGRESS,
            source="市政府常务会议",
            creator_id=admin_user.id,
            responsible_department_id=dept2.id,
            deadline=datetime.now() + timedelta(days=30),
            completion_rate=60,
            is_public=True,
            is_key=True
        )
        
        db.add(supervision_item)
        db.commit()
        
        print("✅ 测试数据创建完成!")
        print("📋 创建的数据:")
        print(f"  - 部门: {db.query(Department).count()}个")
        print(f"  - 角色: {db.query(Role).count()}个") 
        print(f"  - 用户: {db.query(User).count()}个")
        print(f"  - 督办事项: {db.query(SupervisionItem).count()}个")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 初始化测试环境...")
    init_test_db()
    create_test_data()
    print("🎉 测试环境初始化完成!")