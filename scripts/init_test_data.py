#!/usr/bin/env python3
"""
初始化测试数据脚本
用于创建演示系统所需的基础数据
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.app.db.session import SessionLocal
from backend.app.models.user import User
from backend.app.models.organization import Department, Role
from backend.app.models.supervision import SupervisionItem, SupervisionStatus, UrgencyLevel, SupervisionType
from backend.app.models.workflow import WorkflowTemplate, WorkflowStatus
from backend.app.core.security import get_password_hash

def create_test_data():
    """创建测试数据"""
    db = SessionLocal()
    
    try:
        print("🚀 开始初始化测试数据...")
        
        # 1. 创建部门
        departments = create_departments(db)
        print(f"✅ 创建了 {len(departments)} 个部门")
        
        # 2. 创建角色
        roles = create_roles(db)
        print(f"✅ 创建了 {len(roles)} 个角色")
        
        # 3. 创建用户
        users = create_users(db, departments, roles)
        print(f"✅ 创建了 {len(users)} 个用户")
        
        # 4. 创建督办事项
        supervision_items = create_supervision_items(db, users, departments)
        print(f"✅ 创建了 {len(supervision_items)} 个督办事项")
        
        # 5. 创建工作流模板
        workflow_templates = create_workflow_templates(db, users)
        print(f"✅ 创建了 {len(workflow_templates)} 个工作流模板")
        
        print("🎉 测试数据初始化完成！")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_departments(db: Session) -> List[Department]:
    """创建部门数据"""
    departments_data = [
        {"name": "市政府办公室", "code": "OFFICE", "description": "市政府办公室"},
        {"name": "发展改革委", "code": "DRC", "description": "发展和改革委员会"},
        {"name": "财政局", "code": "FINANCE", "description": "财政局"},
        {"name": "人力资源社会保障局", "code": "HRSS", "description": "人力资源和社会保障局"},
        {"name": "自然资源局", "code": "NATURAL", "description": "自然资源局"},
        {"name": "生态环境局", "code": "ECOLOGY", "description": "生态环境局"},
        {"name": "住房城乡建设局", "code": "HOUSING", "description": "住房和城乡建设局"},
        {"name": "交通运输局", "code": "TRANSPORT", "description": "交通运输局"},
        {"name": "教育局", "code": "EDUCATION", "description": "教育局"},
        {"name": "卫生健康委", "code": "HEALTH", "description": "卫生健康委员会"}
    ]
    
    departments = []
    for i, dept_data in enumerate(departments_data):
        # 检查是否已存在
        existing = db.query(Department).filter(Department.code == dept_data["code"]).first()
        if existing:
            departments.append(existing)
            continue
            
        department = Department(
            name=dept_data["name"],
            code=dept_data["code"],
            description=dept_data["description"],
            level=1,
            sort_order=i + 1,
            is_active=True
        )
        db.add(department)
        departments.append(department)
    
    db.commit()
    return departments

def create_roles(db: Session) -> List[Role]:
    """创建角色数据"""
    roles_data = [
        {"name": "系统管理员", "code": "ADMIN", "description": "系统管理员，拥有所有权限"},
        {"name": "督查专员", "code": "SUPERVISOR", "description": "督查专员，负责督办事项管理"},
        {"name": "部门负责人", "code": "DEPT_MANAGER", "description": "部门负责人，管理本部门督办事项"},
        {"name": "普通用户", "code": "USER", "description": "普通用户，处理分配的任务"},
        {"name": "审核员", "code": "REVIEWER", "description": "审核员，负责督办事项审核"},
    ]
    
    roles = []
    for i, role_data in enumerate(roles_data):
        # 检查是否已存在
        existing = db.query(Role).filter(Role.code == role_data["code"]).first()
        if existing:
            roles.append(existing)
            continue
            
        role = Role(
            name=role_data["name"],
            code=role_data["code"],
            description=role_data["description"],
            is_builtin=True,
            sort_order=i + 1
        )
        db.add(role)
        roles.append(role)
    
    db.commit()
    return roles

def create_users(db: Session, departments: List[Department], roles: List[Role]) -> List[User]:
    """创建用户数据"""
    users_data = [
        {
            "username": "admin",
            "real_name": "系统管理员",
            "email": "admin@example.com",
            "phone": "13800138000",
            "employee_id": "ADMIN001",
            "position": "系统管理员",
            "password": "admin123456",
            "role_code": "ADMIN",
            "dept_code": "OFFICE"
        },
        {
            "username": "supervisor",
            "real_name": "张督查",
            "email": "supervisor@example.com",
            "phone": "13800138001",
            "employee_id": "SUP001",
            "position": "督查专员",
            "password": "sup123456",
            "role_code": "SUPERVISOR",
            "dept_code": "OFFICE"
        },
        {
            "username": "manager1",
            "real_name": "李主任",
            "email": "manager1@example.com",
            "phone": "13800138002",
            "employee_id": "MGR001",
            "position": "发改委主任",
            "password": "mgr123456",
            "role_code": "DEPT_MANAGER",
            "dept_code": "DRC"
        },
        {
            "username": "manager2",
            "real_name": "王局长",
            "email": "manager2@example.com",
            "phone": "13800138003",
            "employee_id": "MGR002",
            "position": "财政局局长",
            "password": "mgr123456",
            "role_code": "DEPT_MANAGER",
            "dept_code": "FINANCE"
        },
        {
            "username": "user1",
            "real_name": "陈办事员",
            "email": "user1@example.com",
            "phone": "13800138004",
            "employee_id": "USER001",
            "position": "办事员",
            "password": "user123456",
            "role_code": "USER",
            "dept_code": "DRC"
        },
        {
            "username": "user2",
            "real_name": "刘科员",
            "email": "user2@example.com",
            "phone": "13800138005",
            "employee_id": "USER002",
            "position": "科员",
            "password": "user123456",
            "role_code": "USER",
            "dept_code": "FINANCE"
        }
    ]
    
    # 创建部门和角色的映射
    dept_map = {dept.code: dept.id for dept in departments}
    role_map = {role.code: role.id for role in roles}
    
    users = []
    for user_data in users_data:
        # 检查是否已存在
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if existing:
            users.append(existing)
            continue
            
        user = User(
            username=user_data["username"],
            real_name=user_data["real_name"],
            email=user_data["email"],
            phone=user_data["phone"],
            employee_id=user_data["employee_id"],
            position=user_data["position"],
            password_hash=get_password_hash(user_data["password"]),
            department_id=dept_map.get(user_data["dept_code"]),
            is_active=True,
            is_superuser=(user_data["role_code"] == "ADMIN")
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    return users

def create_supervision_items(db: Session, users: List[User], departments: List[Department]) -> List[SupervisionItem]:
    """创建督办事项数据"""
    # 获取用户和部门映射
    admin_user = next((u for u in users if u.username == "admin"), users[0])
    supervisor_user = next((u for u in users if u.username == "supervisor"), users[0])
    
    supervision_data = [
        {
            "title": "推进重大项目建设进度",
            "content": "督办各部门重大项目建设进度，确保按时完成年度目标任务。包括基础设施建设、产业项目建设等重点项目的推进情况。",
            "type": SupervisionType.KEY,
            "urgency": UrgencyLevel.HIGH,
            "status": SupervisionStatus.IN_PROGRESS,
            "source": "市政府常务会议",
            "creator_id": supervisor_user.id,
            "responsible_department_id": departments[1].id,  # 发改委
            "deadline": datetime.now() + timedelta(days=30)
        },
        {
            "title": "优化营商环境专项行动",
            "content": "深化'放管服'改革，优化营商环境，提升政务服务效率。重点推进政务服务'一网通办'、企业开办便利化等工作。",
            "type": SupervisionType.SPECIAL,
            "urgency": UrgencyLevel.MEDIUM,
            "status": SupervisionStatus.PENDING,
            "source": "市委市政府决定",
            "creator_id": supervisor_user.id,
            "responsible_department_id": departments[0].id,  # 办公室
            "deadline": datetime.now() + timedelta(days=45)
        },
        {
            "title": "环保督察整改落实",
            "content": "按照中央环保督察要求，督办各责任部门落实整改措施，确保环保问题整改到位。",
            "type": SupervisionType.EMERGENCY,
            "urgency": UrgencyLevel.HIGH,
            "status": SupervisionStatus.IN_PROGRESS,
            "source": "中央环保督察组",
            "creator_id": supervisor_user.id,
            "responsible_department_id": departments[5].id,  # 生态环境局
            "deadline": datetime.now() + timedelta(days=15)
        },
        {
            "title": "民生实事项目推进",
            "content": "督办年度民生实事项目实施进度，包括教育、医疗、住房等领域的重点民生项目。",
            "type": SupervisionType.REGULAR,
            "urgency": UrgencyLevel.MEDIUM,
            "status": SupervisionStatus.COMPLETED,
            "source": "政府工作报告",
            "creator_id": supervisor_user.id,
            "responsible_department_id": departments[3].id,  # 人社局
            "deadline": datetime.now() - timedelta(days=10),
            "actual_completion_date": datetime.now() - timedelta(days=5)
        },
        {
            "title": "安全生产专项检查",
            "content": "开展安全生产专项检查，督办各部门落实安全生产责任制，消除安全隐患。",
            "type": SupervisionType.REGULAR,
            "urgency": UrgencyLevel.HIGH,
            "status": SupervisionStatus.OVERDUE,
            "source": "安委会决定",
            "creator_id": supervisor_user.id,
            "responsible_department_id": departments[6].id,  # 住建局
            "deadline": datetime.now() - timedelta(days=5)
        }
    ]
    
    supervision_items = []
    for i, item_data in enumerate(supervision_data):
        # 生成督办编号
        number = f"DB{datetime.now().year}{(i+1):04d}"
        
        item = SupervisionItem(
            number=number,
            title=item_data["title"],
            content=item_data["content"],
            type=item_data["type"],
            urgency=item_data["urgency"],
            status=item_data["status"],
            source=item_data["source"],
            creator_id=item_data["creator_id"],
            responsible_department_id=item_data["responsible_department_id"],
            deadline=item_data["deadline"],
            actual_completion_date=item_data.get("actual_completion_date"),
            completion_rate=90 if item_data["status"] == SupervisionStatus.COMPLETED else 
                           60 if item_data["status"] == SupervisionStatus.IN_PROGRESS else 0,
            is_public=True,
            is_key=(item_data["type"] == SupervisionType.KEY)
        )
        db.add(item)
        supervision_items.append(item)
    
    db.commit()
    return supervision_items

def create_workflow_templates(db: Session, users: List[User]) -> List[WorkflowTemplate]:
    """创建工作流模板数据"""
    admin_user = next((u for u in users if u.username == "admin"), users[0])
    
    templates_data = [
        {
            "name": "督办事项审批流程",
            "code": "SUPERVISION_APPROVAL",
            "description": "督办事项从创建到完成的标准审批流程",
            "type": "supervision",
            "definition": {
                "nodes": [
                    {"id": "start", "name": "开始", "type": "start"},
                    {"id": "review", "name": "部门审核", "type": "task"},
                    {"id": "approve", "name": "领导审批", "type": "task"},
                    {"id": "execute", "name": "执行任务", "type": "task"},
                    {"id": "complete", "name": "完成", "type": "end"}
                ],
                "transitions": [
                    {"from": "start", "to": "review", "name": "提交审核"},
                    {"from": "review", "to": "approve", "name": "审核通过"},
                    {"from": "approve", "to": "execute", "name": "审批通过"},
                    {"from": "execute", "to": "complete", "name": "执行完成"}
                ]
            }
        },
        {
            "name": "重点督办流程",
            "code": "KEY_SUPERVISION",
            "description": "重点督办事项的特殊处理流程",
            "type": "key_supervision",
            "definition": {
                "nodes": [
                    {"id": "start", "name": "开始", "type": "start"},
                    {"id": "urgent_review", "name": "紧急审核", "type": "task"},
                    {"id": "leader_approve", "name": "主要领导审批", "type": "task"},
                    {"id": "track", "name": "跟踪执行", "type": "task"},
                    {"id": "report", "name": "进度汇报", "type": "task"},
                    {"id": "complete", "name": "完成", "type": "end"}
                ],
                "transitions": [
                    {"from": "start", "to": "urgent_review", "name": "紧急提交"},
                    {"from": "urgent_review", "to": "leader_approve", "name": "审核通过"},
                    {"from": "leader_approve", "to": "track", "name": "批准执行"},
                    {"from": "track", "to": "report", "name": "定期汇报"},
                    {"from": "report", "to": "complete", "name": "完成任务"}
                ]
            }
        }
    ]
    
    templates = []
    for template_data in templates_data:
        # 检查是否已存在
        existing = db.query(WorkflowTemplate).filter(
            WorkflowTemplate.code == template_data["code"]
        ).first()
        if existing:
            templates.append(existing)
            continue
            
        template = WorkflowTemplate(
            name=template_data["name"],
            code=template_data["code"],
            description=template_data["description"],
            type=template_data["type"],
            version="1.0",
            is_enabled=True,
            is_builtin=True,
            definition=template_data["definition"],
            creator_id=admin_user.id
        )
        db.add(template)
        templates.append(template)
    
    db.commit()
    return templates

if __name__ == "__main__":
    try:
        create_test_data()
        print("\n🎯 测试数据初始化成功完成！")
        print("\n默认账户信息:")
        print("管理员: admin / admin123456")
        print("督查员: supervisor / sup123456")
        print("部门主任: manager1 / mgr123456")
        print("普通用户: user1 / user123456")
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        sys.exit(1)