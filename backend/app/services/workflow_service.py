from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from datetime import datetime, timedelta
import uuid
import json

from app.models.workflow import (
    WorkflowTemplate, WorkflowInstance, WorkflowNode, WorkflowTransition,
    WorkflowStatus, NodeType, NodeStatus
)
from app.models.user import User, Role
from app.models.organization import Department
from app.schemas.workflow import (
    WorkflowTemplateCreate, WorkflowTemplateUpdate,
    WorkflowInstanceCreate, WorkflowInstanceUpdate,
    WorkflowNodeCreate, WorkflowNodeUpdate
)


class WorkflowService:
    """工作流服务类"""

    def __init__(self, db: Session):
        self.db = db

    # ========== 工作流模板管理 ==========
    
    def create_template(self, template_data: WorkflowTemplateCreate, creator_id: str) -> WorkflowTemplate:
        """创建工作流模板"""
        template = WorkflowTemplate(
            name=template_data.name,
            code=template_data.code,
            description=template_data.description,
            type=template_data.type,
            version=template_data.version or "1.0",
            definition=template_data.definition,
            form_config=template_data.form_config,
            permission_config=template_data.permission_config,
            notification_config=template_data.notification_config,
            is_enabled=template_data.is_enabled,
            creator_id=creator_id
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def get_template_list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        keyword: Optional[str] = None,
        type_filter: Optional[str] = None,
        is_enabled: Optional[bool] = None
    ) -> tuple[List[WorkflowTemplate], int]:
        """获取工作流模板列表"""
        query = self.db.query(WorkflowTemplate)
        
        # 添加筛选条件
        if keyword:
            query = query.filter(
                or_(
                    WorkflowTemplate.name.ilike(f"%{keyword}%"),
                    WorkflowTemplate.code.ilike(f"%{keyword}%"),
                    WorkflowTemplate.description.ilike(f"%{keyword}%")
                )
            )
        
        if type_filter:
            query = query.filter(WorkflowTemplate.type == type_filter)
            
        if is_enabled is not None:
            query = query.filter(WorkflowTemplate.is_enabled == is_enabled)
        
        # 获取总数
        total = query.count()
        
        # 分页和排序
        templates = query.order_by(desc(WorkflowTemplate.created_at)).offset(skip).limit(limit).all()
        
        return templates, total

    def get_template_by_id(self, template_id: str) -> Optional[WorkflowTemplate]:
        """根据ID获取工作流模板"""
        return self.db.query(WorkflowTemplate).filter(WorkflowTemplate.id == template_id).first()

    def get_template_by_code(self, code: str) -> Optional[WorkflowTemplate]:
        """根据代码获取工作流模板"""
        return self.db.query(WorkflowTemplate).filter(WorkflowTemplate.code == code).first()

    def update_template(self, template_id: str, template_data: WorkflowTemplateUpdate) -> Optional[WorkflowTemplate]:
        """更新工作流模板"""
        template = self.get_template_by_id(template_id)
        if not template:
            return None
            
        update_data = template_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)
        
        self.db.commit()
        self.db.refresh(template)
        return template

    def delete_template(self, template_id: str) -> bool:
        """删除工作流模板"""
        template = self.get_template_by_id(template_id)
        if not template:
            return False
            
        # 检查是否有正在运行的实例
        running_instances = self.db.query(WorkflowInstance).filter(
            and_(
                WorkflowInstance.template_id == template_id,
                WorkflowInstance.status.in_([WorkflowStatus.DRAFT, WorkflowStatus.ACTIVE])
            )
        ).count()
        
        if running_instances > 0:
            raise ValueError("无法删除模板，存在正在运行的工作流实例")
        
        self.db.delete(template)
        self.db.commit()
        return True

    # ========== 工作流实例管理 ==========
    
    def create_instance(self, instance_data: WorkflowInstanceCreate, initiator_id: str) -> WorkflowInstance:
        """创建工作流实例"""
        # 获取模板
        template = self.get_template_by_id(instance_data.template_id)
        if not template:
            raise ValueError("工作流模板不存在")
        
        # 生成实例编号
        instance_number = self._generate_instance_number(template.code)
        
        # 创建实例
        instance = WorkflowInstance(
            number=instance_number,
            title=instance_data.title,
            template_id=instance_data.template_id,
            initiator_id=initiator_id,
            business_id=instance_data.business_id,
            business_type=instance_data.business_type,
            business_data=instance_data.business_data,
            variables=instance_data.variables or {},
            priority=instance_data.priority or 1,
            status=WorkflowStatus.DRAFT
        )
        
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        
        # 初始化工作流节点
        self._initialize_workflow_nodes(instance, template)
        
        return instance

    def start_instance(self, instance_id: str, user_id: str) -> bool:
        """启动工作流实例"""
        instance = self.get_instance_by_id(instance_id)
        if not instance:
            return False
            
        if instance.status != WorkflowStatus.DRAFT:
            raise ValueError("只能启动草稿状态的工作流实例")
        
        # 更新实例状态
        instance.status = WorkflowStatus.ACTIVE
        instance.start_time = datetime.utcnow()
        
        # 激活开始节点
        start_nodes = self.db.query(WorkflowNode).filter(
            and_(
                WorkflowNode.workflow_instance_id == instance_id,
                WorkflowNode.type == NodeType.START
            )
        ).all()
        
        for node in start_nodes:
            node.status = NodeStatus.ACTIVE
            node.enter_time = datetime.utcnow()
        
        self.db.commit()
        
        # 自动流转到下一个节点
        self._auto_flow_to_next_nodes(instance, start_nodes, user_id)
        
        return True

    def get_instance_list(
        self,
        skip: int = 0,
        limit: int = 100,
        keyword: Optional[str] = None,
        status_filter: Optional[WorkflowStatus] = None,
        initiator_id: Optional[str] = None,
        template_id: Optional[str] = None,
        business_type: Optional[str] = None
    ) -> tuple[List[WorkflowInstance], int]:
        """获取工作流实例列表"""
        query = self.db.query(WorkflowInstance)
        
        # 添加筛选条件
        if keyword:
            query = query.filter(
                or_(
                    WorkflowInstance.title.ilike(f"%{keyword}%"),
                    WorkflowInstance.number.ilike(f"%{keyword}%")
                )
            )
        
        if status_filter:
            query = query.filter(WorkflowInstance.status == status_filter)
            
        if initiator_id:
            query = query.filter(WorkflowInstance.initiator_id == initiator_id)
            
        if template_id:
            query = query.filter(WorkflowInstance.template_id == template_id)
            
        if business_type:
            query = query.filter(WorkflowInstance.business_type == business_type)
        
        # 获取总数
        total = query.count()
        
        # 分页和排序
        instances = query.order_by(desc(WorkflowInstance.created_at)).offset(skip).limit(limit).all()
        
        return instances, total

    def get_instance_by_id(self, instance_id: str) -> Optional[WorkflowInstance]:
        """根据ID获取工作流实例"""
        return self.db.query(WorkflowInstance).filter(WorkflowInstance.id == instance_id).first()

    def get_user_tasks(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[NodeStatus] = None
    ) -> tuple[List[WorkflowNode], int]:
        """获取用户的待办任务"""
        # 获取用户及其角色、部门信息
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return [], 0
        
        query = self.db.query(WorkflowNode).join(WorkflowInstance)
        
        # 构建任务分配条件
        conditions = [
            WorkflowNode.assignee_id == user_id,  # 直接分配给用户
        ]
        
        # 如果用户有角色，添加角色条件
        if hasattr(user, 'roles') and user.roles:
            role_ids = [role.id for role in user.roles]
            conditions.append(WorkflowNode.assignee_role_id.in_(role_ids))
        
        # 如果用户有部门，添加部门条件
        if user.department_id:
            conditions.append(WorkflowNode.assignee_department_id == user.department_id)
        
        query = query.filter(or_(*conditions))
        
        # 只查询活动的工作流实例
        query = query.filter(WorkflowInstance.status == WorkflowStatus.ACTIVE)
        
        # 状态筛选
        if status_filter:
            query = query.filter(WorkflowNode.status == status_filter)
        else:
            query = query.filter(WorkflowNode.status.in_([NodeStatus.PENDING, NodeStatus.ACTIVE]))
        
        # 获取总数
        total = query.count()
        
        # 分页和排序
        tasks = query.order_by(desc(WorkflowNode.enter_time)).offset(skip).limit(limit).all()
        
        return tasks, total

    # ========== 任务处理 ==========
    
    def complete_task(
        self,
        task_id: str,
        user_id: str,
        form_data: Optional[Dict[str, Any]] = None,
        comment: Optional[str] = None
    ) -> bool:
        """完成任务"""
        task = self.db.query(WorkflowNode).filter(WorkflowNode.id == task_id).first()
        if not task:
            return False
        
        # 检查任务状态
        if task.status not in [NodeStatus.PENDING, NodeStatus.ACTIVE]:
            raise ValueError("任务状态不允许完成操作")
        
        # 检查权限（简化版本，实际应该更复杂）
        if not self._check_task_permission(task, user_id):
            raise ValueError("没有权限处理此任务")
        
        # 更新任务
        task.status = NodeStatus.COMPLETED
        task.processor_id = user_id
        task.complete_time = datetime.utcnow()
        if task.start_time is None:
            task.start_time = datetime.utcnow()
        
        if form_data:
            task.form_data = form_data
        if comment:
            task.comment = comment
        
        # 记录转换日志
        self._log_transition(task.workflow_instance_id, task.node_id, None, user_id, f"完成任务: {task.name}")
        
        self.db.commit()
        
        # 流转到下一个节点
        instance = task.workflow_instance
        self._auto_flow_to_next_nodes(instance, [task], user_id)
        
        return True

    # ========== 私有方法 ==========
    
    def _generate_instance_number(self, template_code: str) -> str:
        """生成工作流实例编号"""
        date_str = datetime.now().strftime("%Y%m%d")
        sequence = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.number.like(f"{template_code}{date_str}%")
        ).count() + 1
        return f"{template_code}{date_str}{sequence:04d}"

    def _initialize_workflow_nodes(self, instance: WorkflowInstance, template: WorkflowTemplate):
        """初始化工作流节点"""
        if not template.definition or 'nodes' not in template.definition:
            return
        
        nodes_config = template.definition['nodes']
        for node_config in nodes_config:
            node = WorkflowNode(
                workflow_instance_id=instance.id,
                node_id=node_config['id'],
                name=node_config['name'],
                type=NodeType(node_config['type']),
                status=NodeStatus.PENDING,
                node_data=node_config.get('data', {}),
                assignee_id=node_config.get('assignee_id'),
                assignee_role_id=node_config.get('assignee_role_id'),
                assignee_department_id=node_config.get('assignee_department_id')
            )
            self.db.add(node)
        
        self.db.commit()

    def _auto_flow_to_next_nodes(self, instance: WorkflowInstance, completed_nodes: List[WorkflowNode], user_id: str):
        """自动流转到下一个节点"""
        if not instance.template.definition or 'transitions' not in instance.template.definition:
            return
        
        transitions_config = instance.template.definition['transitions']
        
        for completed_node in completed_nodes:
            # 查找从当前节点出发的转换
            next_transitions = [
                t for t in transitions_config 
                if t['from'] == completed_node.node_id
            ]
            
            for transition in next_transitions:
                # 检查转换条件（简化版本）
                if self._check_transition_condition(transition, instance, completed_node):
                    # 激活目标节点
                    target_node = self.db.query(WorkflowNode).filter(
                        and_(
                            WorkflowNode.workflow_instance_id == instance.id,
                            WorkflowNode.node_id == transition['to']
                        )
                    ).first()
                    
                    if target_node and target_node.status == NodeStatus.PENDING:
                        target_node.status = NodeStatus.ACTIVE
                        target_node.enter_time = datetime.utcnow()
                        
                        # 如果是结束节点，完成工作流
                        if target_node.type == NodeType.END:
                            instance.status = WorkflowStatus.COMPLETED
                            instance.end_time = datetime.utcnow()
                        
                        # 记录转换
                        self._log_transition(
                            instance.id, 
                            completed_node.node_id, 
                            target_node.node_id, 
                            user_id,
                            transition.get('name', '自动流转')
                        )
        
        self.db.commit()

    def _check_transition_condition(self, transition: Dict, instance: WorkflowInstance, node: WorkflowNode) -> bool:
        """检查转换条件（简化版本）"""
        # 这里应该实现更复杂的条件检查逻辑
        # 目前只是简单返回True
        return True

    def _check_task_permission(self, task: WorkflowNode, user_id: str) -> bool:
        """检查任务处理权限（简化版本）"""
        # 直接分配给用户
        if task.assignee_id == user_id:
            return True
        
        # 通过角色分配
        if task.assignee_role_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user and hasattr(user, 'roles'):
                user_role_ids = [role.id for role in user.roles]
                if task.assignee_role_id in user_role_ids:
                    return True
        
        # 通过部门分配
        if task.assignee_department_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user and user.department_id == task.assignee_department_id:
                return True
        
        return False

    def _log_transition(
        self, 
        instance_id: str, 
        from_node_id: Optional[str], 
        to_node_id: Optional[str], 
        user_id: str, 
        comment: str
    ):
        """记录工作流转换日志"""
        transition = WorkflowTransition(
            workflow_instance_id=instance_id,
            from_node_id=from_node_id,
            to_node_id=to_node_id,
            executor_id=user_id,
            comment=comment,
            execute_time=datetime.utcnow()
        )
        self.db.add(transition)


# 创建服务实例的工厂函数
def get_workflow_service(db: Session) -> WorkflowService:
    """获取工作流服务实例"""
    return WorkflowService(db)