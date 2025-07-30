from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.models.supervision import (
    SupervisionItem, TaskAssignment, ProgressReport, StatusLog,
    SupervisionType, SupervisionStatus, SupervisionUrgency, TaskStatus
)
from app.models.user import User
from app.models.organization import Department
from app.schemas.supervision import (
    SupervisionItemCreate, SupervisionItemUpdate,
    TaskAssignmentCreate, TaskAssignmentUpdate,
    ProgressReportCreate, ProgressReportUpdate,
    StatusLogCreate, SupervisionEvaluationCreate
)


def generate_supervision_number() -> str:
    """生成督办编号"""
    import time
    timestamp = int(time.time() * 1000)
    import random
    random_num = random.randint(1000, 9999)
    return f"DB{timestamp}{random_num}"


# 督办事项管理
def get_supervision_item(db: Session, item_id: UUID) -> Optional[SupervisionItem]:
    """根据ID获取督办事项"""
    return db.query(SupervisionItem).filter(
        SupervisionItem.id == item_id,
        SupervisionItem.is_deleted == False
    ).first()


def get_supervision_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    type: SupervisionType = None,
    status: SupervisionStatus = None,
    urgency: SupervisionUrgency = None,
    creator_id: UUID = None,
    responsible_department_id: UUID = None,
    is_key: bool = None,
    start_date_from: datetime = None,
    start_date_to: datetime = None,
    deadline_from: datetime = None,
    deadline_to: datetime = None
) -> List[SupervisionItem]:
    """获取督办事项列表"""
    query = db.query(SupervisionItem).filter(SupervisionItem.is_deleted == False)
    
    if search:
        query = query.filter(
            or_(
                SupervisionItem.title.contains(search),
                SupervisionItem.content.contains(search),
                SupervisionItem.number.contains(search)
            )
        )
    
    if type:
        query = query.filter(SupervisionItem.type == type)
    
    if status:
        query = query.filter(SupervisionItem.status == status)
    
    if urgency:
        query = query.filter(SupervisionItem.urgency == urgency)
    
    if creator_id:
        query = query.filter(SupervisionItem.creator_id == creator_id)
    
    if responsible_department_id:
        query = query.filter(SupervisionItem.responsible_department_id == responsible_department_id)
    
    if is_key is not None:
        query = query.filter(SupervisionItem.is_key == is_key)
    
    if start_date_from:
        query = query.filter(SupervisionItem.start_date >= start_date_from)
    
    if start_date_to:
        query = query.filter(SupervisionItem.start_date <= start_date_to)
    
    if deadline_from:
        query = query.filter(SupervisionItem.deadline >= deadline_from)
    
    if deadline_to:
        query = query.filter(SupervisionItem.deadline <= deadline_to)
    
    return query.order_by(desc(SupervisionItem.created_at)).offset(skip).limit(limit).all()


def count_supervision_items(
    db: Session,
    search: str = None,
    type: SupervisionType = None,
    status: SupervisionStatus = None,
    urgency: SupervisionUrgency = None,
    creator_id: UUID = None,
    responsible_department_id: UUID = None,
    is_key: bool = None,
    start_date_from: datetime = None,
    start_date_to: datetime = None,
    deadline_from: datetime = None,
    deadline_to: datetime = None
) -> int:
    """统计督办事项数量"""
    query = db.query(SupervisionItem).filter(SupervisionItem.is_deleted == False)
    
    if search:
        query = query.filter(
            or_(
                SupervisionItem.title.contains(search),
                SupervisionItem.content.contains(search),
                SupervisionItem.number.contains(search)
            )
        )
    
    if type:
        query = query.filter(SupervisionItem.type == type)
    
    if status:
        query = query.filter(SupervisionItem.status == status)
    
    if urgency:
        query = query.filter(SupervisionItem.urgency == urgency)
    
    if creator_id:
        query = query.filter(SupervisionItem.creator_id == creator_id)
    
    if responsible_department_id:
        query = query.filter(SupervisionItem.responsible_department_id == responsible_department_id)
    
    if is_key is not None:
        query = query.filter(SupervisionItem.is_key == is_key)
    
    if start_date_from:
        query = query.filter(SupervisionItem.start_date >= start_date_from)
    
    if start_date_to:
        query = query.filter(SupervisionItem.start_date <= start_date_to)
    
    if deadline_from:
        query = query.filter(SupervisionItem.deadline >= deadline_from)
    
    if deadline_to:
        query = query.filter(SupervisionItem.deadline <= deadline_to)
    
    return query.count()


def create_supervision_item(
    db: Session, 
    item_create: SupervisionItemCreate, 
    creator_id: UUID
) -> SupervisionItem:
    """创建督办事项"""
    db_item = SupervisionItem(
        number=generate_supervision_number(),
        title=item_create.title,
        content=item_create.content,
        type=item_create.type,
        urgency=item_create.urgency,
        status=SupervisionStatus.DRAFT,
        creator_id=creator_id,
        responsible_department_id=item_create.responsible_department_id,
        cooperating_departments=item_create.cooperating_departments or [],
        source=item_create.source,
        start_date=item_create.start_date,
        deadline=item_create.deadline,
        expected_result=item_create.expected_result,
        is_public=item_create.is_public,
        is_key=item_create.is_key,
        tags=item_create.tags or [],
        completion_rate=0
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # 创建状态变更日志
    create_status_log(
        db=db,
        supervision_item_id=db_item.id,
        operator_id=creator_id,
        action_type="create",
        old_status=None,
        new_status=SupervisionStatus.DRAFT.value,
        reason="创建督办事项"
    )
    
    return db_item


def update_supervision_item(
    db: Session,
    item_id: UUID,
    item_update: SupervisionItemUpdate,
    operator_id: UUID
) -> Optional[SupervisionItem]:
    """更新督办事项"""
    db_item = get_supervision_item(db, item_id)
    if not db_item:
        return None
    
    update_data = item_update.dict(exclude_unset=True)
    old_status = db_item.status
    
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db_item.updated_by = operator_id
    db.commit()
    db.refresh(db_item)
    
    # 如果状态发生变化，记录日志
    if 'status' in update_data and update_data['status'] != old_status:
        create_status_log(
            db=db,
            supervision_item_id=item_id,
            operator_id=operator_id,
            action_type="status_change",
            old_status=old_status.value if old_status else None,
            new_status=update_data['status'].value,
            reason="更新督办状态"
        )
    
    return db_item


def delete_supervision_item(db: Session, item_id: UUID, operator_id: UUID) -> bool:
    """删除督办事项（软删除）"""
    db_item = get_supervision_item(db, item_id)
    if not db_item:
        return False
    
    db_item.is_deleted = True
    db_item.deleted_at = datetime.utcnow()
    db_item.updated_by = operator_id
    db.commit()
    
    return True


def change_supervision_status(
    db: Session,
    item_id: UUID,
    new_status: SupervisionStatus,
    operator_id: UUID,
    reason: str = None
) -> Optional[SupervisionItem]:
    """更改督办状态"""
    db_item = get_supervision_item(db, item_id)
    if not db_item:
        return None
    
    old_status = db_item.status
    db_item.status = new_status
    db_item.updated_by = operator_id
    
    # 如果完成，设置完成时间
    if new_status == SupervisionStatus.COMPLETED:
        db_item.actual_completion_date = datetime.utcnow()
        db_item.completion_rate = 100
    
    db.commit()
    db.refresh(db_item)
    
    # 记录状态变更日志
    create_status_log(
        db=db,
        supervision_item_id=item_id,
        operator_id=operator_id,
        action_type="status_change",
        old_status=old_status.value,
        new_status=new_status.value,
        reason=reason or f"状态从{old_status.value}变更为{new_status.value}"
    )
    
    return db_item


def evaluate_supervision_item(
    db: Session,
    item_id: UUID,
    evaluation: SupervisionEvaluationCreate,
    evaluator_id: UUID
) -> Optional[SupervisionItem]:
    """评价督办事项"""
    db_item = get_supervision_item(db, item_id)
    if not db_item:
        return None
    
    # 计算总体评分
    overall_score = (
        evaluation.quality_score + 
        evaluation.efficiency_score + 
        evaluation.satisfaction_score
    ) / 3
    
    db_item.quality_score = evaluation.quality_score
    db_item.efficiency_score = evaluation.efficiency_score
    db_item.satisfaction_score = evaluation.satisfaction_score
    db_item.overall_score = overall_score
    db_item.evaluation_comment = evaluation.evaluation_comment
    db_item.updated_by = evaluator_id
    
    db.commit()
    db.refresh(db_item)
    
    # 记录评价日志
    create_status_log(
        db=db,
        supervision_item_id=item_id,
        operator_id=evaluator_id,
        action_type="evaluate",
        old_status=None,
        new_status="evaluated",
        reason="督办事项评价",
        extra_data={
            "quality_score": evaluation.quality_score,
            "efficiency_score": evaluation.efficiency_score,
            "satisfaction_score": evaluation.satisfaction_score,
            "overall_score": overall_score
        }
    )
    
    return db_item


# 任务分配管理
def get_task_assignment(db: Session, task_id: UUID) -> Optional[TaskAssignment]:
    """根据ID获取任务分配"""
    return db.query(TaskAssignment).filter(
        TaskAssignment.id == task_id,
        TaskAssignment.is_deleted == False
    ).first()


def get_task_assignments_by_supervision(
    db: Session, 
    supervision_item_id: UUID
) -> List[TaskAssignment]:
    """获取督办事项的任务分配列表"""
    return db.query(TaskAssignment).filter(
        TaskAssignment.supervision_item_id == supervision_item_id,
        TaskAssignment.is_deleted == False
    ).all()


def create_task_assignment(
    db: Session,
    task_create: TaskAssignmentCreate,
    assigner_id: UUID
) -> TaskAssignment:
    """创建任务分配"""
    db_task = TaskAssignment(
        supervision_item_id=task_create.supervision_item_id,
        title=task_create.title,
        description=task_create.description,
        assignee_id=task_create.assignee_id,
        assigned_department_id=task_create.assigned_department_id,
        status=TaskStatus.ASSIGNED,
        priority=task_create.priority,
        start_date=task_create.start_date,
        deadline=task_create.deadline,
        estimated_hours=task_create.estimated_hours,
        notes=task_create.notes,
        completion_rate=0,
        created_by=assigner_id
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task


def update_task_assignment(
    db: Session,
    task_id: UUID,
    task_update: TaskAssignmentUpdate,
    operator_id: UUID
) -> Optional[TaskAssignment]:
    """更新任务分配"""
    db_task = get_task_assignment(db, task_id)
    if not db_task:
        return None
    
    update_data = task_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db_task.updated_by = operator_id
    db.commit()
    db.refresh(db_task)
    
    return db_task


def accept_task_assignment(db: Session, task_id: UUID, assignee_id: UUID) -> Optional[TaskAssignment]:
    """接收任务分配"""
    db_task = get_task_assignment(db, task_id)
    if not db_task or db_task.assignee_id != assignee_id:
        return None
    
    db_task.status = TaskStatus.ACCEPTED
    db_task.start_date = datetime.utcnow()
    db_task.updated_by = assignee_id
    
    db.commit()
    db.refresh(db_task)
    
    return db_task


def complete_task_assignment(
    db: Session, 
    task_id: UUID, 
    assignee_id: UUID,
    actual_hours: float = None
) -> Optional[TaskAssignment]:
    """完成任务分配"""
    db_task = get_task_assignment(db, task_id)
    if not db_task or db_task.assignee_id != assignee_id:
        return None
    
    db_task.status = TaskStatus.COMPLETED
    db_task.completion_date = datetime.utcnow()
    db_task.completion_rate = 100
    if actual_hours:
        db_task.actual_hours = actual_hours
    db_task.updated_by = assignee_id
    
    db.commit()
    db.refresh(db_task)
    
    # 更新督办事项的完成率
    update_supervision_completion_rate(db, db_task.supervision_item_id)
    
    return db_task


# 进度报告管理
def get_progress_report(db: Session, report_id: UUID) -> Optional[ProgressReport]:
    """根据ID获取进度报告"""
    return db.query(ProgressReport).filter(
        ProgressReport.id == report_id,
        ProgressReport.is_deleted == False
    ).first()


def get_progress_reports_by_supervision(
    db: Session,
    supervision_item_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[ProgressReport]:
    """获取督办事项的进度报告列表"""
    return db.query(ProgressReport).filter(
        ProgressReport.supervision_item_id == supervision_item_id,
        ProgressReport.is_deleted == False
    ).order_by(desc(ProgressReport.report_date)).offset(skip).limit(limit).all()


def create_progress_report(
    db: Session,
    report_create: ProgressReportCreate,
    reporter_id: UUID
) -> ProgressReport:
    """创建进度报告"""
    db_report = ProgressReport(
        supervision_item_id=report_create.supervision_item_id,
        task_assignment_id=report_create.task_assignment_id,
        reporter_id=reporter_id,
        title=report_create.title,
        content=report_create.content,
        progress_rate=report_create.progress_rate,
        completed_work=report_create.completed_work,
        next_plan=report_create.next_plan,
        issues=report_create.issues,
        support_needed=report_create.support_needed,
        estimated_completion=report_create.estimated_completion,
        risk_assessment=report_create.risk_assessment,
        is_important=report_create.is_important,
        report_date=datetime.utcnow(),
        created_by=reporter_id
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # 更新督办事项或任务的进度
    if report_create.task_assignment_id:
        # 更新任务进度
        task = get_task_assignment(db, report_create.task_assignment_id)
        if task:
            task.completion_rate = report_create.progress_rate
            task.updated_by = reporter_id
            db.commit()
    
    # 更新督办事项的完成率
    update_supervision_completion_rate(db, report_create.supervision_item_id)
    
    return db_report


def update_progress_report(
    db: Session,
    report_id: UUID,
    report_update: ProgressReportUpdate,
    operator_id: UUID
) -> Optional[ProgressReport]:
    """更新进度报告"""
    db_report = get_progress_report(db, report_id)
    if not db_report:
        return None
    
    update_data = report_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_report, field, value)
    
    db_report.updated_by = operator_id
    db.commit()
    db.refresh(db_report)
    
    return db_report


# 状态日志管理
def create_status_log(
    db: Session,
    supervision_item_id: UUID,
    operator_id: UUID,
    action_type: str,
    old_status: str = None,
    new_status: str = None,
    reason: str = None,
    extra_data: dict = None
) -> StatusLog:
    """创建状态变更日志"""
    db_log = StatusLog(
        supervision_item_id=supervision_item_id,
        operator_id=operator_id,
        action_type=action_type,
        old_status=old_status,
        new_status=new_status,
        reason=reason,
        action_time=datetime.utcnow(),
        extra_data=extra_data or {},
        created_by=operator_id
    )
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    return db_log


def get_status_logs_by_supervision(
    db: Session,
    supervision_item_id: UUID
) -> List[StatusLog]:
    """获取督办事项的状态变更日志"""
    return db.query(StatusLog).filter(
        StatusLog.supervision_item_id == supervision_item_id,
        StatusLog.is_deleted == False
    ).order_by(desc(StatusLog.action_time)).all()


# 统计分析
def update_supervision_completion_rate(db: Session, supervision_item_id: UUID):
    """更新督办事项的完成率"""
    supervision_item = get_supervision_item(db, supervision_item_id)
    if not supervision_item:
        return
    
    # 获取所有任务分配
    tasks = get_task_assignments_by_supervision(db, supervision_item_id)
    
    if not tasks:
        # 没有任务分配，基于进度报告计算
        latest_report = db.query(ProgressReport).filter(
            ProgressReport.supervision_item_id == supervision_item_id,
            ProgressReport.is_deleted == False
        ).order_by(desc(ProgressReport.report_date)).first()
        
        if latest_report:
            supervision_item.completion_rate = latest_report.progress_rate
    else:
        # 基于任务完成率计算
        total_progress = sum(task.completion_rate for task in tasks)
        supervision_item.completion_rate = int(total_progress / len(tasks))
    
    db.commit()


def get_supervision_stats(db: Session, department_id: UUID = None) -> dict:
    """获取督办统计数据"""
    query = db.query(SupervisionItem).filter(SupervisionItem.is_deleted == False)
    
    if department_id:
        query = query.filter(SupervisionItem.responsible_department_id == department_id)
    
    total_count = query.count()
    pending_count = query.filter(SupervisionItem.status == SupervisionStatus.PENDING).count()
    in_progress_count = query.filter(SupervisionItem.status == SupervisionStatus.IN_PROGRESS).count()
    completed_count = query.filter(SupervisionItem.status == SupervisionStatus.COMPLETED).count()
    overdue_count = query.filter(
        SupervisionItem.status != SupervisionStatus.COMPLETED,
        SupervisionItem.deadline < datetime.utcnow()
    ).count()
    
    completion_rate = completed_count / total_count * 100 if total_count > 0 else 0
    
    # 计算平均效率评分
    avg_efficiency = db.query(func.avg(SupervisionItem.efficiency_score)).filter(
        SupervisionItem.is_deleted == False,
        SupervisionItem.efficiency_score.isnot(None)
    ).scalar() or 0
    
    urgent_count = query.filter(SupervisionItem.urgency == SupervisionUrgency.HIGH).count()
    key_count = query.filter(SupervisionItem.is_key == True).count()
    
    return {
        "total_count": total_count,
        "pending_count": pending_count,
        "in_progress_count": in_progress_count,
        "completed_count": completed_count,
        "overdue_count": overdue_count,
        "completion_rate": round(completion_rate, 2),
        "average_efficiency_score": round(avg_efficiency, 2),
        "urgent_count": urgent_count,
        "key_count": key_count
    }


def get_department_stats(db: Session) -> List[dict]:
    """获取各部门统计数据"""
    departments = db.query(Department).filter(Department.is_deleted == False).all()
    stats = []
    
    for dept in departments:
        dept_stats = get_supervision_stats(db, dept.id)
        stats.append({
            "department_id": dept.id,
            "department_name": dept.name,
            **dept_stats
        })
    
    return stats


def get_overdue_items(db: Session, limit: int = 50) -> List[SupervisionItem]:
    """获取逾期督办事项"""
    return db.query(SupervisionItem).filter(
        SupervisionItem.is_deleted == False,
        SupervisionItem.status != SupervisionStatus.COMPLETED,
        SupervisionItem.deadline < datetime.utcnow()
    ).order_by(SupervisionItem.deadline).limit(limit).all()


def get_urgent_items(db: Session, limit: int = 50) -> List[SupervisionItem]:
    """获取紧急督办事项"""
    return db.query(SupervisionItem).filter(
        SupervisionItem.is_deleted == False,
        SupervisionItem.urgency == SupervisionUrgency.HIGH,
        SupervisionItem.status.in_([SupervisionStatus.PENDING, SupervisionStatus.IN_PROGRESS])
    ).order_by(SupervisionItem.deadline).limit(limit).all()